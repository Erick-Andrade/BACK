### Import Packages
import time
import oci
import json
import re

from oci.ai_vision import AIServiceVisionClient
from oci.ai_vision.models.create_image_job_details import CreateImageJobDetails
from oci.ai_vision.models.image_object_detection_feature import ImageObjectDetectionFeature
from oci.ai_vision.models.input_location import InputLocation
from oci.ai_vision.models.object_list_inline_input_location import ObjectListInlineInputLocation
from oci.ai_vision.models.object_location import ObjectLocation
from oci.ai_vision.models.object_storage_document_details import ObjectStorageDocumentDetails
from oci.ai_vision.models.output_location import OutputLocation
from oci.object_storage import ObjectStorageClient

### Define Variables
namespace_name = "ModeloAlgodaoDefinitivo" 
bucket_name = "bucketPragas"
compartment_id = "ocid1.tenancy.oc1..aaaaaaaa2coodpgxxxqrtjmobsbz6jesjaghapg3jo5fxyz5gwpsfv4laxsa"
input_prefix = "Sample-Images"
output_prefix = "Final-Results"
max_results_per_image = 25

# Auth Config Definition
config = oci.config.from_file('.oci/config')

# AI Vision Client Definition
ai_vision_client = oci.ai_vision.AIServiceVisionClient(config)

### Get Images from Object Storage Using Object Storage Client
# List Objects in Bucket
object_storage_client = ObjectStorageClient(config)


### Get Images from Object Storage Using Object Storage Client
# List Objects in Bucket
object_list = object_storage_client.list_objects(
    
### Get Images from Object Storage Using Object Storage Client
# List Objects in Bucket
object_list = object_storage_client.list_objects(
    namespace_name = namespace_name,
    bucket_name = bucket_name,
    prefix = input_prefix
)
)