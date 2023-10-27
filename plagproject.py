import nltk
from googlesearch import search
import requests
import cgi, os
import cgitb; cgitb.enable()
import shutil
form = cgi.FieldStorage()
from flask import request
from fpdf import FPDF
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
# from werkzeug import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from wtforms import Form, TextField, validators
from nltk.tokenize import sent_tokenize, word_tokenize
from difflib import SequenceMatcher
from statistics import mean
import shutil
import os
from subprocess import Popen, PIPE
from wtforms.validators import DataRequired
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# FLASK APP CONFIG
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "7d441f27d441f27567d441f2b6176a"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


class ReusableForm(Form):
    name = TextField("Name:", validators=[DataRequired()])


@app.route("/", methods=["GET", "POST"])
def hello():
    global wel
    form = ReusableForm(request.form)
    f = open("Corpus.txt", "w")  # File to store live streaming data-corpus
    g = open("Report.txt", "w")  # file to store plagiarism report
    input1 = open("file1.txt", "w")  # file to store textarea content
    h = open("input.txt", "w")  # file to take input file
    try:

        def search1(line):
            print("searching started")
            g.write(line)
            g.write("\n")
            for url in search(line, stop=2):
                if url != " ":
                    print(url)
                    g.write(url)
                    g.write("\n")
                    r = requests.get(url)  # search in google
                    soup = BeautifulSoup(r.content, "html.parser")
                    rows = soup.find_all("p")
                    for row in rows:
                        f.write(row.get_text())
                        f.write("\n")
                else:
                    flash("No plagiarism found")

            print("Urlsearch completed for {}".format(line))
    except ConnectionError as e:
        print("Error")

    # Function to download plagiarism report from webpage
    def download_file():
        path = "url.txt"
        return send_file(path, as_attachment=True)

    # function to compute similarity between two files
    def similarity():
        text1 = open("Corpus.txt").read()
        print("similarity checking")
        text2 = s
        print(text2)
        # Create a TF-IDF vectorizer    
        vectorizer = CountVectorizer()
        # Fit and transform the documents into TF vectors
        tf_matrix = vectorizer.fit_transform([text1, text2])
        # Compute cosine similarity between the TF vectors
        cosine_sim = cosine_similarity(tf_matrix[0], tf_matrix[1])[0][0]
        # Calculating plagiarism percentage
        plag_percent = cosine_sim * 100 
        
        return plag_percent

    # upload button
    if request.method == "POST":
        
        if "filename" in request.files and request.files["filename"].filename != "":
            file = request.files["filename"]
            file_ext = file.filename.rsplit(".", 1)[-1].lower() #splitting the extension of file uploaded

        # For txt document files
            if file_ext == "txt" :
                file_path = "uploaded.txt"
                file.save(file_path)
                print("txt file uploaded")
                s = read_txtfile(file_path)
                lines = sent_tokenize(s)
                for line in lines:
                    search1(line)
                wel = similarity()
                return render_template("index.html",wel=wel, text_content=s)

        # For OpenDocument Text (ODT) files
            elif file_ext == "odt":
                file_path = "uploaded.odt"
                file.save(file_path)
                print("ODT file uploaded")
                s = read_odt_file(file_path)
                lines = sent_tokenize(s)
                for line in lines:
                    search1(line)
                wel = similarity()
                return render_template("index.html",wel=wel, text_content=s)

        # For doc files            
            elif file_ext == "doc":
                file_path = "uploaded.doc"
                file.save(file_path)
                print("DOC file uploaded")
                s = read_doc_file(file_path)
                lines = sent_tokenize(s)
                for line in lines:
                    search1(line)
                wel = similarity()
                return render_template("index.html",wel=wel, text_content=s)

        # search function to seach using google API

        elif request.form["check"]:
            name = request.form["text"]
            f1 = open("file1.txt", "w")
            f1.write(name)
            f1.close()
            file1 = open("file1.txt", "r")
            s = file1.read()
            lines = sent_tokenize(s)
            for line in lines:
                search1(line)
            wel = similarity()

            return render_template("index.html",wel=wel, text_content=name)

    return render_template("index.html")

# function for txt file 

def read_txtfile(file_path):
    with open(file_path) as f:
        contents = f.read()
    return contents
    
# function for odt conversion

def read_odt_file(file_path):
    cmd = ["odt2txt", file_path]
    p = Popen(cmd, stdout=PIPE)
    stdout, stderr = p.communicate()
    return stdout.decode("utf-8", "ignore")

# function for doc conversion

def read_doc_file(file_path):
    cmd = ['antiword', file_path]
    p = Popen(cmd, stdout=PIPE)
    stdout, stderr = p.communicate()
    return stdout.decode("utf-8", "ignore")




@app.route("/download")
def download_file():  # to download report from webpage
    path = "/home/parvathy/Desktop/plag/Report.txt"

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)
