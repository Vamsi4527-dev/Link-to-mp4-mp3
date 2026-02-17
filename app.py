from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
import os

app = Flask(__name__)


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
    yt = YouTube(link)
    stream = yt.streams.get_highest_resolution()
    file_path = stream.download()

    return send_file(file_path, as_attachment=True)


@app.route("/downloadmp3")
def download_mp3():
    link = request.args.get("link")
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    file_path = stream.download()

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
