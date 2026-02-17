import os
from flask import Flask, render_template, request, send_file, after_this_request
from pytubefix import YouTube

# Configure app for Vercel
# We use root-relative paths for templates and static folders
app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

@app.route("/")
def landing():
    return render_template("main.html")

@app.route("/index")
def converter():
    return render_template("index.html")

@app.route("/youtube/api", methods=["POST"])
def convert():
    link = request.form["link_input"].strip()
    file_type = request.form["file_type"]

    try:
        yt = YouTube(link)
        yt.check_availability()

        title = yt.title
        author = yt.author
        thumbnail = yt.thumbnail_url
        length = yt.length

        return render_template("result.html",
                               title=title,
                               author=author,
                               thumbnail_url=thumbnail,
                               length=length,
                               link_input=link,
                               ftype=file_type)

    except Exception as e:
        print("ERROR:", e)  
        return render_template("error.html",
                               error_message=str(e))

@app.route("/download")
def download_video():
    link = request.args.get("link")
    try:
        yt = YouTube(link)
        stream = yt.streams.get_highest_resolution()
        
        # Download to /tmp for Vercel compatibility
        download_dir = "/tmp"
        if not os.path.exists(download_dir):
            download_dir = "."
            
        file_path = stream.download(output_path=download_dir)
        
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as error:
                app.logger.error(f"Error removing file: {error}")
            return response

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return render_template("error.html", error_message=str(e))

@app.route("/downloadmp3")
def download_mp3():
    link = request.args.get("link")
    try:
        yt = YouTube(link)
        stream = yt.streams.filter(only_audio=True).first()
        
        # Download to /tmp for Vercel compatibility
        download_dir = "/tmp"
        if not os.path.exists(download_dir):
            download_dir = "."
            
        file_path = stream.download(output_path=download_dir)

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as error:
                app.logger.error(f"Error removing file: {error}")
            return response

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return render_template("error.html", error_message=str(e))

# For local development
if __name__ == "__main__":
    app.run(debug=True)
