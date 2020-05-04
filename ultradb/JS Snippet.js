<script>(function() {
    document.getElementById("color_sheet").onchange = function(){
      var files = document.getElementById("color_sheet").files;
      var file = files[0];
      if(!file){
        return alert("No file selected.");
      }
      getSignedRequest(file);
    };
  })();</script>

  <script>function getSignedRequest(file){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/sign_s3?file_name="+file.name+"&file_type="+file.type);
    xhr.onreadystatechange = function(){
      if(xhr.readyState === 4){
        if(xhr.status === 200){
          var response = JSON.parse(xhr.responseText);
          uploadFile(file, response.data, response.url);
        }
        else{
          alert("Could not get signed URL.");
        }
      }
    };
    xhr.send();
  }</script>

  <script>function uploadFile(file, s3Data, url){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", s3Data.url);
  
    var postData = new FormData();
    for(key in s3Data.fields){
      postData.append(key, s3Data.fields[key]);
    }
    postData.append('file', file);
  
    xhr.onreadystatechange = function() {
      if(xhr.readyState === 4){
        if(xhr.status === 200 || xhr.status === 204){
          console.log("Set cs_url block")
          document.getElementById("cs_url").value = url;
        }
        else{
          console.log(postData)
          alert("Could not upload file.");
        }
     }
    };
    xhr.send(postData);
  }</script>



# S3 direct upload route
@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = os.environ.get('AWS_STORAGE_BUCKET_NAME')

  file_name = request.args.get('file_name')
  file_type = request.args.get('file_type')

  s3 = boto3.client('s3')

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"Content-Type": file_type},
    Conditions = [
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })



  # # Upload to S3
# @app.route('/upload', methods=['POST'])
# def upload_to_S3():
#     bucket='upaintdb-colorsheets'
#     myfile = request.files['myfile']
#     file_name = myfile.filename
#     print(file_name)
#     upload_file(file_name, bucket)

#     # s3 = boto3.resource('s3')

#     # s3.Bucket('upaintdb-colorsheets').put_object(Key='an_image.jpg', Body=request.files['myfile'])
    
#     # return "<h1>File uploaded to S3</h1>"

# # Test route for S3 upload
# @app.route('/test')
# def test():
#     return"""<form method =POST enctype=multipart/form-data action="upload">
#     <input type=file name=myfile>
#     <input type=submit>
#     </form>"""