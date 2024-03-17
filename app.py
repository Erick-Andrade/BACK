import base64
import io
import oci
import time
import json
from flask import Flask, request
from oci.ai_vision import AIServiceVisionClient
from oci.object_storage import ObjectStorageClient
from PIL import Image



app = Flask(__name__)

@app.route("/")
def index():
    return "Ok"

@app.route("/upload", methods=['POST'])
def upload():
    namespace_name = "grkjou41lac1"
    bucket_name = "pidaydemo"

    config = oci.config.from_file('~/.oci/config')

    dados = request.json
    imagem_base64 = dados['image'] 
    imagem_bytes = base64.b64decode(imagem_base64)
    with open('imagem_recebida.jpg', 'wb') as f:
        f.write(imagem_bytes)

    # Abra a imagem
    image = Image.open('imagem_recebida.jpg')

    # Redimensione a imagem para a largura e altura desejadas
    nova_largura = 422
    nova_altura = 303
    imagem_redimensionada = image.resize((nova_largura, nova_altura))
    imagem_redimensionada.save('imagem_recebida.jpg')

    # Feche a imagem original
    image.close()

    object_storage = oci.object_storage.ObjectStorageClient(config)

    local_file_name = "imagem_recebida.jpg"
    object_name = "imagem_recebida.jpg"
    with open(local_file_name, 'rb') as f:
        image_data = f.read()   
    object_storage.put_object(
        namespace_name=namespace_name,
        bucket_name=bucket_name,
        object_name=object_name,
        put_object_body=io.BytesIO(image_data)
    )


    return "Ok"



@app.route("/ai_vision")
def ai_vision():
    namespace_name = "grkjou41lac1"
    bucket_name = "pidaydemo"
    model_id = "ocid1.aivisionmodel.oc1.sa-saopaulo-1.amaaaaaafgrfu6aatzgaz7ggaw7u6dhzbsohqx6ldydzzhzmkaqkxmc3uiga"

    config = oci.config.from_file('~/.oci/config')
    MAX_RESULTS = 5
    ai_vision_client = AIServiceVisionClient(config)

    # Setup image_classification_feature
    image_classification_feature = oci.ai_vision.models.ImageClassificationFeature()
    image_classification_feature.model_id = model_id
    image_classification_feature.max_results = MAX_RESULTS
    features = [image_classification_feature]


    # Setup input locations
    object_location_1 = oci.ai_vision.models.ObjectLocation()
    object_location_1.namespace_name = namespace_name
    object_location_1.bucket_name = bucket_name
    object_location_1.object_name = "imagem_recebida.jpg"


    object_locations = [object_location_1]
    input_location = oci.ai_vision.models.ObjectListInlineInputLocation()
    input_location.object_locations = object_locations


    # Setup output locations
    output_location = oci.ai_vision.models.OutputLocation()
    output_location.namespace_name = namespace_name
    output_location.bucket_name = bucket_name
    output_location.prefix = "Output"

    # Ai Vision
    create_image_job_details = oci.ai_vision.models.CreateImageJobDetails()
    create_image_job_details.features = features
    create_image_job_details.compartment_id = "ocid1.tenancy.oc1..aaaaaaaa2coodpgxxxqrtjmobsbz6jesjaghapg3jo5fxyz5gwpsfv4laxsa"
    create_image_job_details.output_location = output_location
    create_image_job_details.input_location = input_location
    create_image_job_details.is_zip_output_enabled = False
    res = ai_vision_client.create_image_job(create_image_job_details=create_image_job_details)


    job_id = res.data.id
    res = ai_vision_client.get_image_job(image_job_id=job_id)

    while res.data.lifecycle_state == "IN_PROGRESS" or res.data.lifecycle_state == "ACCEPTED":
        res = ai_vision_client.get_image_job(image_job_id=job_id)

    object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
    res = ai_vision_client.get_image_job(image_job_id=job_id)

    for object_location in object_locations:
        namespace = output_location.namespace_name
        bucket = output_location.bucket_name
        object_name = "{}/{}/{}_{}_{}.json".format(output_location.prefix, job_id, namespace, bucket,
                                                object_location.object_name)
        byte_array = download_object_from_object_storage(object_storage_client, namespace, bucket, object_name)
        json_result = json.dumps(json.loads(byte_array.read()))
        analyzeImageResult = ai_vision_client.base_client.deserialize_response_data(json_result.encode('utf8'),
                                                                                            "AnalyzeImageResult")
        
    labels = analyzeImageResult.labels
    result = dict()
    for label in labels:
        result[label.name] = label.confidence

    result_json = json.dumps(result)

    return result_json



def download_object_from_object_storage(object_storage_client: ObjectStorageClient, namespace: str, bucket: str,
                            source_object_name: str) -> io.BytesIO:
    response = object_storage_client.get_object(namespace, bucket, source_object_name)
    if response.status == 200:
        byte_array: io.BytesIO = io.BytesIO()
        for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
            byte_array.write(chunk)
        byte_array.seek(0)
        return byte_array   



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)