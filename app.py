import requests
import oci
from flask import Flask
from oci.ai_vision import AIServiceVisionClient
from oci.ai_vision.models import ImageClassificationFeature, AnalyzeImageDetails, InlineImageDetails


app = Flask(__name__)
namespace_name = "grkjou41lac1" 
bucket_name = "pidaydemo"

config = oci.config.from_file('~/.oci/config')
vision_client = AIServiceVisionClient(config)

@app.route("/")
def index():

    return "Hello"

@app.route("/upload", methods=['POST'])
def upload(image):
    if 'image' not in requests.files:
        return "Nenhuma imagem encontrada", 400
    
    image_file = requests.files['image']
    image_file.save('imagem_recebida.jpg')

    # Manda para a IA

    return image_file


    # Recebe seu resultado



def classify_image(image_data):
    model__id = "ocid1.oc1.sa-saopaulo1.amaaaaaafgrfu6aaaffadwrrvr3ldf6fddkb3t3f4uf422ednk3umzi4z67a"
    image_content = open(image_data, 'rb').read()
    compartment__id = "ocid1.bucket.oc1.sa-saopaulo-1.aaaaaaaaxh5kmaamuvafi4wkxv4d2q3v5dipzmnecxkumzdzeiozqs4djc3"
    
    analyze_image_response = vision_client.analyze_image(
        analyze_image_details = AnalyzeImageDetails(
            compartment_id=compartment__id,
            features=[
                ImageClassificationFeature(
                    feature_type="IMAGE_CLASSIFICATION",
                    model_id=model__id
                )],
            image=InlineImageDetails(
                source="INLINE",
                data=image_data)
            )
    )

    
    return analyze_image_response


if __name__ == "__main__":
    #image_file_path = "folha.jpg"
    #classify_image(image_file_path)
    #result = classify_image(image_file_path)
    #print(result.data)
    app.run(host="0.0.0.0", port=5555, debug=True)