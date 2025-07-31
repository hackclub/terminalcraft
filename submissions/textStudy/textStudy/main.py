import typer
import whisper
import os
from imageio_ffmpeg import get_ffmpeg_exe
import ffmpeg
import transformers
from pathlib import Path
import yt_dlp
from datetime import datetime, timedelta
import uuid
from rich.progress import track
import semantic_text_splitter
from tokenizers import Tokenizer
from transformers import pipeline
import weasyprint
import requests
import textwrap
import json

CONFIG_FILE = os.path.expanduser("~/.textstudy_config.json")

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def get_video_info():
    """Get current video information from config"""
    config = load_config()
    return config.get('path', ''), config.get('vdir', ''), config.get('vname', '')

def set_video_info(path, vdir, vname):
    """Save video information to config"""
    config = load_config()
    config.update({
        'path': path,
        'vdir': vdir,
        'vname': vname
    })
    save_config(config)


def setup_ffmpeg():
    """Setup FFmpeg path for cross-platform compatibility"""
    try:
        ffmpeg_path = get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        

        current_path = os.environ.get("PATH", "")
        if ffmpeg_dir not in current_path:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path
        
        ffmpeg._run.DEFAULT_FFMPEG_PATH = ffmpeg_path
        
        return ffmpeg_path
    except Exception as e:
        typer.echo(f"Error setting up FFmpeg: {e}")
        return None


ffmpeg_executable = setup_ffmpeg()

audioready = False
textready = False
path = ""
Vdir = ""
Vname = ""
Apath = ""
transcribtion = ""

class progressHook:
    def __init__(self , progress , task_id):
        self.progress = progress
        self.task_id = task_id

    def __call__(self , d):
        if d['state'] == 'downloading':
            if 'total_bytes' in d:
                total = d['total_bytes']
                downloaded = d['downloaded_bytes']
                self.progress.update(self.task_id , total = total , completed = downloaded)
            elif 'total_bytes_estimate' in d:
                total = d['total_bytes_estimate']
                downloaded = d['downloaded_bytes']
                self.progress.update(self.task_id , total = total , completed = downloaded)
        elif d['state'] == 'finished':
            self.progress.update(self.task_id , completed = d.get('total_bytes' , 100) , total = d.get('total_bytes' , 100))

def markDown(text, functionU):
    mdPath = os.path.splitext(path)[0] + functionU + ".md"
    with open(mdPath,"w", encoding="utf-8") as m:
        m.write("#generated content\n\n")
        for i, line in enumerate(text.split("\n"), 1):
            if line.strip():
                m.write(f"{i}. {line.strip()}\n\n")

def pdf(text, functionU):
    pdfPath = os.path.splitext(path)[0]+functionU+".pdf"
    headd = "generated content"
    html = f"""
<html>
<head>
    <meta charset="utf-8">
    <style>
    body {{font-family: 'Georgia', serif; padding: 1em; border-radius: 5px; overflow: auto; }}
    h1 {{ text-align: center; color: #003366;}}
    h2 {{ color: #005588; margin-top: 1.5em; }}
    pre {{ background: #f4f4f4; padding: 1em; border-radius: 5px; overflow-x: auto; }}
    code {{ background: #f0f0f0; padding: 1em; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<h1>{headd}</h1>
<pre>{text.strip()}</pre>
</html>
"""
    weasyprint.HTML(string=html).write_pdf(pdfPath)
    pass


def LaTeX(text, functionU):
    latexPath = os.path.splitext(path)[0]+ functionU +".tex"
    with open(latexPath,"w", encoding="utf-8") as l:
        l.write(r"""\documentclass{article}
\usepackage[utf-8]{inputenc}
\usepackage{enumitem}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{geometry}
\geometry{margin=1in}
\title{Generated Content}
\date{\today}
\begin{document}
\maketitle
""")
        safeText = (
            text.replace("&",r"\&")
                .replace("%",r"\%")
                .replace("#",r"\#")
                .replace("_",r"\_")
                .replace("~",r"\textasciitilde{}")
                .replace("^",r"\textasciicircum{}")
                .replace("\\",r"\textbackslash{}")
        )
        l.write(safeText.strip())
        l.write(r"\end{document}")

def downloadVideo(Vlink):
    global path, Vdir, Vname
    dir = Path.cwd()
    Vdir = dir / "videos"
    Vdir.mkdir(exist_ok=True)
    nowTime = datetime.now().strftime("%Y%m%d_%H%M%S")
    uID = uuid.uuid4().hex[:6]
    Vname = f"%(title).50s_{nowTime}_{uID}.%(ext)s"

    temp_path = Vdir / Vname
    ydl_opts = {
        'outtmpl': str(temp_path),
        'format': 'bestvideo[height<=480]+bestaudio/best',
        'merge_output_format': 'mp4',
        "cookiesfrombrowser": ("chrome",),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([Vlink])
        except Exception as e:
            typer.echo(f"unavaliable URL: {e}")
            return None,None,None

    
    path = None
    for file in Vdir.glob(f"*{nowTime}_{uID}*"):
        if file.is_file() and file.suffix.lower() in ('.mp4' ,'.mkv' , '.avi' ,'.mov','webm'):
            path = str(file)
            break
    if path:
        Vname = os.path.basename(path)
        return str(Vdir), Vname , path
    else:
        typer.echo("Downloaded file not found")
        return None,None,None


def video2audio(Vpath, Vdir):

    global audioready
    
    if not ffmpeg_executable:
        typer.echo("FFmpeg not available. Please install it or check your imageio-ffmpeg installation.")
        return None
    
    Apath = os.path.splitext(Vpath)[0] + ".wav"
    
    try:

        stream = ffmpeg.input(Vpath)
        stream = ffmpeg.output(
            stream,
            Apath,
            format='wav',
            acodec='pcm_s16le',
            ac=1,
            ar='16000'
        )
        
        ffmpeg.run(stream, cmd=ffmpeg_executable, overwrite_output=True, quiet=True)
        audioready = True
        return Apath
        
    except Exception as e:
        typer.echo(f"Error converting video to audio: {e}")
        return None


def audio2text(audioPath, language: str = "auto"):
    global textready, transcribtion
    model = whisper.load_model('base')
    if language == "auto":
        transcribtion = model.transcribe(audioPath)
    else:
        transcribtion = model.transcribe(audioPath, language=language, task="translate")

    txt_path = os.path.splitext(audioPath)[0] + ".txt"
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcribtion["text"].strip())
    except Exception as e:
        typer.echo(f"Warning: Could not save transcript: {e}")

    textready = True
    return transcribtion


def summary(transcribtion: str, ratio: int):
    """Enhanced summary function with better text processing and models"""
    
    cleanText = transcribtion.strip()
    maxTokens = 1024
    summaries = []
    
    try:
        modelName = "facebook/bart-large-cnn"
        sumTokenizer = transformers.BartTokenizer.from_pretrained(modelName)
        model = transformers.BartForConditionalGeneration.from_pretrained(modelName)
    except:
        modelName = "sshleifer/distilbart-cnn-12-6"
        sumTokenizer = transformers.BartTokenizer.from_pretrained(modelName)
        model = transformers.BartForConditionalGeneration.from_pretrained(modelName)
    
    splitTokenizer = Tokenizer.from_pretrained("bert-base-uncased")
    splitter = semantic_text_splitter.TextSplitter.from_huggingface_tokenizer(splitTokenizer, maxTokens)
    chunks = splitter.chunks(cleanText)
    
    try:
        cleaner = pipeline("text2text-generation", model="google/flan-t5-large")
    except:
        cleaner = pipeline("text2text-generation", model="google/flan-t5-base")
    
    cleaned_chunks = []
    
    for chunk in chunks:
        cleanPrompt = f"Clean and improve this transcript text to be more readable and well-structured: {chunk}"
        try:
            cleaned = cleaner(cleanPrompt, max_length=512, do_sample=False)[0]['generated_text']
            cleaned_chunks.append(cleaned)
        except:
            cleaned_chunks.append(chunk)
    
    for paragraph in cleaned_chunks:
        if not paragraph.strip():
            continue
            
        wordsNumber = len(paragraph.split())
        if wordsNumber < 10:
            continue
            
        maximumOut = min(150, max(50, int(wordsNumber / ratio)))
        minimumOut = max(20, int(wordsNumber / (ratio * 2)))
        
        summary_prompt = f"Summarize the following text concisely while preserving key information: {paragraph}"
        
        try:
            inputs = sumTokenizer.encode(summary_prompt, return_tensors="pt", max_length=512, truncation=True)
            summaryIds = model.generate(
                inputs, 
                max_length=maximumOut, 
                min_length=minimumOut, 
                length_penalty=1.0, 
                num_beams=4, 
                early_stopping=True,
                temperature=0.7
            )
            Fsummary = sumTokenizer.decode(summaryIds[0], skip_special_tokens=True)
            summaries.append(Fsummary)
        except Exception as e:
            typer.echo(f"Warning: Error summarizing chunk: {e}")
            sentences = paragraph.split('.')
            fallback_summary = '. '.join(sentences[:2]) + '.'
            summaries.append(fallback_summary)
    
    if summaries:
        FFsummary = "\n\n".join(summaries)
        typer.echo("Your summary:\n" + "="*50 + "\n" + FFsummary + "\n" + "="*50)
        return FFsummary
    else:
        typer.echo("No summary could be generated.")
        return ""

def paraphrase(transcribtion:str, fileType, tAPI: bool= False, API:str = None, apiModel:str = None, apiKey:str =None):
    """Enhanced paraphrase function with better prompts and processing for educational content"""
    
    if fileType == "pdf":
        fftype = "plain text formatted for printable PDF with clear sections and professional formatting."
    elif fileType == "markdown":
        fftype = """
- Format output in **Markdown** with proper structure
- Use ## for main sections and ### for subsections
- Include bullet points and numbered lists where appropriate
- Use **bold** for emphasis and `code` for technical terms
- Create a table of contents if the content is long"""
    elif fileType == "latex":
        fftype = """
- Format output in **LaTeX** with proper document structure
- Use \\section*{name} for main sections and \\subsection*{name} for subsections
- Use \\begin{enumerate} for numbered lists and \\begin{itemize} for bullet points
- Include \\begin{verbatim} for code blocks
- Use proper LaTeX formatting for mathematical expressions"""

    maxTokens = 2048
    
    if tAPI:
        chunks = textwrap.wrap(transcribtion, width=3000, break_long_words=False, break_on_hyphens=False)
    else:
        splitTokenizer = Tokenizer.from_pretrained("bert-base-uncased")
        splitter = semantic_text_splitter.TextSplitter.from_huggingface_tokenizer(splitTokenizer, maxTokens)
        chunks = splitter.chunks(transcribtion)
    
    Fchunks = []
    
    base_prompt = f"""You are an expert educational content creator with deep knowledge in multiple subjects. Your task is to transform a video transcript into comprehensive, well-structured educational content.

IMPORTANT REQUIREMENTS:
1. Maintain ALL the original information and concepts from the transcript
2. Organize content logically with clear sections and subsections
3. Add educational value through explanations, examples, and context
4. Use professional, academic writing style
5. Ensure the content is suitable for students and learners
6. Include key takeaways and important points
7. Make complex concepts accessible and understandable

CONTENT STRUCTURE GUIDELINES:
- Start with a brief introduction or overview
- Organize content into logical sections
- Use clear headings and subheadings
- Include bullet points for key concepts
- Add numbered lists for step-by-step processes
- Highlight important terms and definitions
- Include examples where appropriate
- End with a summary or conclusion

FORMAT REQUIREMENTS:
{fftype}

ORIGINAL TRANSCRIPT:
\"\"\"
{{chunk}}
\"\"\"

Create comprehensive educational content that covers ALL the material from the transcript while making it more structured, clear, and educational."""

    for i, chunk in enumerate(chunks):
        context_info = f"\n\n[This is part {i+1} of {len(chunks)} from the complete transcript]"
        prompt = base_prompt.format(chunk=chunk + context_info)
        
        if tAPI:
            try:
                if API.lower() == "huggingface":
                    headers = {"Authorization": f"Bearer {apiKey}"}
                    url = f"https://api-inference.huggingface.co/models/{apiModel}"
                    response = requests.post(url, headers=headers, json={"inputs": prompt})
                    text = response.json()
                    result = text[0]['generated_text'] if isinstance(text, list) else text.get("generated_text", "")

                elif API.lower() == "cohere":
                    headers = {"Authorization": f"Bearer {apiKey}"}
                    url = "https://api.cohere.ai/generate"
                    payload = {
                        "model": apiModel, 
                        "prompt": prompt, 
                        "max_tokens": 1500, 
                        "temperature": 0.3,
                        "k": 0,
                        "stop_sequences": [],
                        "return_likelihoods": "NONE"
                    }
                    response = requests.post(url, headers=headers, json=payload)
                    result = response.json()['generations'][0]['text']

                elif API.lower() == "replicate":
                    headers = {"Authorization": f"Token {apiKey}", "Content-Type": "application/json"}
                    url = "https://api.replicate.com/v1/predictions"
                    payload = {"version": apiModel, "input": {"prompt": prompt}}
                    response = requests.post(url, headers=headers, json=payload)
                    prediction = response.json()
                    result = prediction.get("output", "[replicate pending...]")
                
                elif API.lower() == "groq":
                    headers = {"Authorization": f"Bearer {apiKey}"}
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    payload = {
                        "model": apiModel, 
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                    response = requests.post(url, headers=headers, json=payload)
                    result = response.json()['choices'][0]['message']['content']

                elif API.lower() == "ollama":
                    url = "http://localhost:11434/api/generate"
                    payload = {"model": apiModel, "prompt": prompt}
                    response = requests.post(url, json=payload, stream=True)
                    chunks_response = []
                    for line in response.iter_lines():
                        if line:
                            part = json.loads(line.decode("utf-8"))
                            chunks_response.append(part.get("response", ""))
                    result = "".join(chunks_response)

                elif API.lower() == "gemini":
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{apiModel}:generateContent?key={apiKey}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(url, headers=headers, json=payload)
                    result = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                
                else: 
                    raise ValueError(f"API '{API}' is not supported. Please check your API configuration.")
                
                Fchunks.append(result.strip())
                
            except Exception as e:
                typer.echo(f"Error with API call: {e}")
                tokenizer = transformers.AutoTokenizer.from_pretrained("google/flan-t5-large")
                model = transformers.AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
                output = model.generate(**inputs, max_new_tokens=1024, temperature=0.3)
                decoded = tokenizer.decode(output[0], skip_special_tokens=True)
                Fchunks.append(decoded.strip())
        else:
            try:
                model_name = "google/flan-t5-xl"
                tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
                model = transformers.AutoModelForSeq2SeqLM.from_pretrained(model_name)
            except:
                tokenizer = transformers.AutoTokenizer.from_pretrained("google/flan-t5-large")
                model = transformers.AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
            
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            output = model.generate(**inputs, max_new_tokens=1024, temperature=0.3, do_sample=True)
            decoded = tokenizer.decode(output[0], skip_special_tokens=True)
            Fchunks.append(decoded.strip())

    Fparaphresed = "\n\n" + "="*50 + "\n\n".join(Fchunks) + "\n\n" + "="*50
    
    if fileType == "pdf":
        pdf(Fparaphresed, "_paraphrased")
    elif fileType == "markdown":
        markDown(Fparaphresed, "_paraphrased")
    elif fileType == "latex":
        LaTeX(Fparaphresed, "_paraphrased")
    
    return Fparaphresed


def transcription(audio, language:str = "auto"):
    """Generate subtitles and embed them in video"""
    if not ffmpeg_executable:
        typer.echo("FFmpeg not available for subtitle generation.")
        return
        
    global path, Vdir, Vname
    if not path or not os.path.exists(path):
        typer.echo("Video path not found. Please set a video first.")
        return

    try:
        model = whisper.load_model('base')
        if language == "auto":
            transcribtion = model.transcribe(audio)
        else:
            transcribtion = model.transcribe(audio, language=language, task="translate")
        
        filePath = os.path.join(Vdir, "subtitle.srt")
        segments = transcribtion["segments"]

        with open(filePath, 'w', encoding='utf-8') as srtFile:
            for segment in segments:

                start_time = str(timedelta(seconds=int(segment['start']))) + ',000'
                end_time = str(timedelta(seconds=int(segment['end']))) + ',000'
                text = segment['text'].strip()
                
                subtitleSeg = f"{segment['id']+1}\n{start_time} --> {end_time}\n{text}\n\n"
                srtFile.write(subtitleSeg)

        baseName, extention = os.path.splitext(Vname)
        output = os.path.join(Vdir, baseName + "_with_subtitles" + extention)
        
        try:
            stream = ffmpeg.input(path)
            
            subtitle_path = filePath.replace('\\', '/').replace(':', '\\:')
            stream = ffmpeg.filter(stream, 'subtitles', subtitle_path)
            

            stream = ffmpeg.output(
                stream, 
                output, 
                vcodec='libx264',
                acodec='copy',
                preset='medium',
                crf=23
            )
            
            ffmpeg.run(stream, cmd=ffmpeg_executable, overwrite_output=True, quiet=True)
            typer.echo(f"✅ Video with subtitles saved as: {output}")
            
        except Exception as e:
            typer.echo(f"❌ Error burning subtitles: {e}")
            typer.echo("Subtitle file created but could not be burned into video.")
            typer.echo(f"Subtitle file location: {filePath}")
            
    except Exception as e:
        typer.echo(f"❌ Error in transcription process: {e}")
        return


def questions(numberQuestions, transcribtion, fileType, style: str = "mcq", tAPI: bool = False, API: str = None, apiModel: str = None, apiKey: str = None):
    """Enhanced questions function with better prompts and intelligent question distribution"""
    
    def questionsPrompt(chunk: str, style: str, Number: int, chunk_info: str):

        style_instructions = {
            "multiple choice": f"""
- Create {Number} multiple choice questions with 4 options (A, B, C, D)
- Each question should have only ONE correct answer
- Make distractors plausible but clearly incorrect
- Include a mix of factual, conceptual, and application questions
- Ensure questions test different levels of understanding""",
            
            "true/false": f"""
- Create {Number} true/false questions
- Ensure a balanced mix of true and false statements
- Make false statements plausible but clearly incorrect
- Focus on key concepts and important facts
- Avoid ambiguous or unclear statements""",
            
            "short answer": f"""
- Create {Number} short answer questions
- Questions should require 1-3 sentences to answer
- Focus on key concepts, definitions, and important facts
- Ask for explanations, examples, or brief analyses
- Ensure questions are specific and clear""",
            
            "essay": f"""
- Create {Number} essay questions
- Questions should require detailed explanations (2-4 paragraphs)
- Focus on analysis, synthesis, and critical thinking
- Ask for comparisons, evaluations, or comprehensive explanations
- Include clear instructions on what to address""",
            
            "fill in the blank": f"""
- Create {Number} fill-in-the-blank questions
- Provide clear context for each blank
- Ensure there is only one correct answer
- Focus on key terms, concepts, and important facts
- Make the context sufficient to determine the answer"""
        }
        
        style_instruction = style_instructions.get(style.lower(), style_instructions["multiple choice"])
        
        return f"""You are an expert educational assessment creator with deep knowledge in creating high-quality questions that effectively test understanding.

TASK: Analyze the following text and generate {Number} {style} questions that comprehensively assess the key concepts, facts, and reasoning presented.

QUALITY REQUIREMENTS:
1. Questions must be clear, unambiguous, and well-written
2. Each question should test a different aspect of the content
3. Questions should range from basic recall to higher-order thinking
4. Ensure questions cover the most important concepts from the text
5. Make questions engaging and educational
6. Avoid trivial or overly simple questions
7. Ensure questions are appropriate for the content level

CONTENT ANALYSIS:
- Identify the main topics and key concepts
- Note important facts, definitions, and relationships
- Consider cause-and-effect relationships
- Look for examples, applications, and implications
- Identify potential misconceptions or challenging areas

{style_instruction}

ORIGINAL TEXT:
\"\"\"
{chunk}
\"\"\"

{chunk_info}

Generate {Number} high-quality {style} questions that thoroughly test understanding of this content."""

    if tAPI:
        chunks = textwrap.wrap(transcribtion, width=2500, break_long_words=False, break_on_hyphens=False)
    else:
        tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
        splitter = semantic_text_splitter.TextSplitter.from_huggingface_tokenizer(tokenizer, max_tokens=2048)
        chunks = splitter.chunks(transcribtion)
    

    chunk_scores = []
    for chunk in chunks:
        words = chunk.split()
        unique_words = len(set(words))
        score = len(words) * 0.3 + unique_words * 0.7
        chunk_scores.append(score)
    
    total_score = sum(chunk_scores)
    questions_per_chunk = []
    
    for score in chunk_scores:
        if total_score > 0:
            questions = max(1, round((score / total_score) * numberQuestions))
            questions_per_chunk.append(questions)
        else:
            questions_per_chunk.append(1)
    
    while sum(questions_per_chunk) > numberQuestions:
        max_idx = questions_per_chunk.index(max(questions_per_chunk))
        questions_per_chunk[max_idx] -= 1
    
    while sum(questions_per_chunk) < numberQuestions:
        min_idx = questions_per_chunk.index(min(questions_per_chunk))
        questions_per_chunk[min_idx] += 1
    
    if fileType == "markdown":
        explainfileType = """
- Format questions in **Markdown**
- Use ## for section headers
- Use **bold** for question numbers: **1.**
- For multiple choice, use:
  - A) Option A
  - B) Option B
  - C) Option C
  - D) Option D
- Use bullet points for lists
- Include answer key at the end"""
    elif fileType == "pdf":
        explainfileType = """
- Write in plain text formatted for printable PDF
- Use clear section headers
- Number questions sequentially
- For multiple choice, use A), B), C), D) format
- Include answer key at the end
- Use proper spacing and formatting"""
    elif fileType == "latex":
        explainfileType = r"""
- Format output in **LaTeX**
- Use \section*{Questions} for headers
- Use \begin{enumerate} for numbered questions
- For multiple choice, use:
  \begin{itemize}
  \item[A)] Option A
  \item[B)] Option B
  \item[C)] Option C
  \item[D)] Option D
  \end{itemize}
- Include answer key at the end"""
    else:
        typer.echo("Unavailable file type. Choose from: markdown, pdf, latex", fg="red")
        return None
    
    connections = []
    
    for i, (chunk, questionsN) in enumerate(zip(chunks, questions_per_chunk)):
        if questionsN <= 0:
            continue
            
        chunk_info = f"[Content from section {i+1} of {len(chunks)}]"
        prompt = questionsPrompt(chunk, style, questionsN, chunk_info)
        
        if tAPI:
            try:
                if API.lower() == "huggingface":
                    headers = {"Authorization": f"Bearer {apiKey}"}
                    url = f"https://api-inference.huggingface.co/models/{apiModel}"
                    response = requests.post(url, headers=headers, json={"inputs": prompt})
                    result = response.json()
                    decoded = result[0]['generated_text'] if isinstance(result, list) else result.get("generated_text", "")

                elif API.lower() == "cohere":
                    headers = {"Authorization": f"Bearer {apiKey}", "Content-Type": "application/json"}
                    url = "https://api.cohere.ai/generate"
                    payload = {
                        "model": apiModel,
                        "prompt": prompt,
                        "max_tokens": 1200,
                        "temperature": 0.3,
                        "k": 0,
                        "stop_sequences": [],
                        "return_likelihoods": "NONE"
                    }
                    response = requests.post(url, headers=headers, json=payload)
                    decoded = response.json()['generations'][0]['text']

                elif API.lower() == "replicate":
                    headers = {"Authorization": f"Token {apiKey}", "Content-Type": "application/json"}
                    url = "https://api.replicate.com/v1/predictions"
                    payload = {
                        "version": apiModel,
                        "input": {"prompt": prompt}
                    }
                    response = requests.post(url, headers=headers, json=payload)
                    result = response.json()
                    decoded = result.get("output", "[replicate pending...]")

                elif API.lower() == "groq":
                    headers = {"Authorization": f"Bearer {apiKey}"}
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    payload = {
                        "model": apiModel,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                    response = requests.post(url, headers=headers, json=payload)
                    decoded = response.json()['choices'][0]['message']['content']

                elif API.lower() == "ollama":
                    url = "http://localhost:11434/api/generate"
                    payload = {"model": apiModel, "prompt": prompt}
                    response = requests.post(url, json=payload, stream=True)
                    parts = [json.loads(line.decode())['response'] for line in response.iter_lines() if line]
                    decoded = "".join(parts)

                elif API.lower() == "gemini":
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{apiModel}:generateContent?key={apiKey}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(url, headers=headers, json=payload)
                    decoded = response.json()["candidates"][0]["content"]["parts"][0]["text"]

                else:
                    raise ValueError(f"API '{API}' is not supported. Please check your API configuration.")
                
                connections.append(decoded.strip())
                
            except Exception as e:
                typer.echo(f"Error with API call: {e}")
                Ftokenizer = transformers.AutoTokenizer.from_pretrained("google/flan-t5-large")
                model = transformers.AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
                inputs = Ftokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
                outputs = model.generate(**inputs, max_new_tokens=1024, temperature=0.3)
                decoded = Ftokenizer.decode(outputs[0], skip_special_tokens=True)
                connections.append(decoded.strip())
        else:
            try:
                model_name = "google/flan-t5-xl"
                Ftokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
                model = transformers.AutoModelForSeq2SeqLM.from_pretrained(model_name)
            except:
                Ftokenizer = transformers.AutoTokenizer.from_pretrained("google/flan-t5-large")
                model = transformers.AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
            
            inputs = Ftokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            outputs = model.generate(**inputs, max_new_tokens=1024, temperature=0.3, do_sample=True)
            decoded = Ftokenizer.decode(outputs[0], skip_special_tokens=True)
            connections.append(decoded.strip())
    
    FfQuestions = "\n\n" + "="*50 + "\n\n".join(connections) + "\n\n" + "="*50
    
    if fileType == "latex":
        LaTeX(FfQuestions, "_questions")
    elif fileType == "pdf":
        pdf(FfQuestions, "_questions")
    elif fileType == "markdown":
        markDown(FfQuestions, "_questions")
    
    return FfQuestions

app = typer.Typer()

@app.command()
def video(vpath: str = typer.Argument(...,help="Video file path or URL"), url : bool = typer.Option(False, "--url", "-u",help="Is this a URL?")):
    global audioready, textready
    audioready = False
    textready = False
    if url :
        link = vpath
        result = downloadVideo(link)
        if result[0] is None:
            typer.echo("Failed to download video")
            return 
        Vdir, path, Vname = result
        set_video_info(path, Vdir, Vname)

    else :
        path = vpath
        Vdir = os.path.dirname(path)
        Vname = os.path.basename(path)
        set_video_info(path,Vdir,Vname)

        typer.echo(f"video set: {Vname}")
        typer.echo(f"Path: {path}")

        return path, Vdir, Vname
    
@app.command()
def addSub(lang : str = typer.Option("auto" , "--lang" , "-l", help="""language is auto the orginal for translate use ISO 639-1 language code
Language	Code
Abkhazian	ab
Afar	aa
Afrikaans	af
Albanian	sq
Amharic	am
Arabic	ar
Armenian	hy
Assamese	as
Aymara	ay
Azerbaijani	az
Bashkir	ba
Basque	eu
Bengali, Bangla	bn
Bhutani	dz
Bihari	bh
Bislama	bi
Breton	br
Bulgarian	bg
Burmese	my
Byelorussian	be
Cambodian	km
Catalan	ca
Chinese	zh
Corsican	co
Croatian	hr
Czech	cs
Danish	da
Dutch	nl
English, American	en
Esperanto	eo
Estonian	et
Faeroese	fo
Fiji	fj
Finnish	fi
French	fr
Frisian	fy
Gaelic (Scots Gaelic)	gd
Galician	gl
Georgian	ka
German	de
Greek	el
Greenlandic	kl
Guarani	gn
Gujarati	gu
Hausa	ha
Hebrew	iw
Hindi	hi
Hungarian	hu
Icelandic	is
Indonesian	in
Interlingua	ia
Interlingue	ie
Inupiak	ik
Irish	ga
Italian	it
Japanese	ja
Javanese	jw
Kannada	kn
Kashmiri	ks
Kazakh	kk
Kinyarwanda	rw
Kirghiz	ky
Kirundi	rn
Korean	ko
Kurdish	ku
Laothian	lo
Latin	la
Latvian, Lettish	lv
Lingala	ln
Lithuanian	lt
Macedonian	mk
Malagasy	mg
Malay	ms
Malayalam	ml
Maltese	mt
Maori	mi
Marathi	mr
Moldavian	mo
Mongolian	mn
Nauru	na
Nepali	ne
Norwegian	no
Occitan	oc
Oriya	or
Oromo, Afan	om
Pashto, Pushto	ps
Persian	fa
Polish	pl
Portuguese	pt
Punjabi	pa
Quechua	qu
Rhaeto-Romance	rm
Romanian	ro
Russian	ru
Samoan	sm
Sangro	sg
Sanskrit	sa
Serbian	sr
Serbo-Croatian	sh
Sesotho	st
Setswana	tn
Shona	sn
Sindhi	sd
Singhalese	si
Siswati	ss
Slovak	sk
Slovenian	sl
Somali	so
Spanish	es
Sudanese	su
Swahili	sw
Swedish	sv
Tagalog	tl
Tajik	tg
Tamil	ta
Tatar	tt
Tegulu	te
Thai	th
Tibetan	bo
Tigrinya	ti
Tonga	to
Tsonga	ts
Turkish	tr
Turkmen	tk
Twi	tw
Ukrainian	uk
Urdu	ur
Uzbek	uz
Vietnamese	vi
Volapuk	vo
Welsh	cy
Wolof	who
Xhosa	xh
Yiddish	ji
Yoruba	yo
Zulu	zu
""")):
    path, Vdir, Vname = get_video_info()
    
    globals()["path"], globals()["Vdir"], globals()["Vname"] = path, Vdir, Vname
    
    if not path or not os.path.exists(path):
        typer.echo("❌ Please set a video first using 'textStudy video <path>' or the video file doesn't exist")
        return
    
    Apath = os.path.splitext(path)[0] + ".wav"
    if not os.path.exists(Apath):
        typer.echo("🔄 Converting video to audio...")
        Apath = video2audio(path, Vdir)
        if not Apath:
            typer.echo("❌ Failed to convert video to audio")
            return
    else:
        typer.echo("✅ Using existing audio file")

    subtitle_file = os.path.join(Vdir, "subtitle.srt")
    if os.path.exists(subtitle_file):
        typer.echo("✅ Subtitle file already exists, proceeding to burn into video...")
        try:
            baseName, extention = os.path.splitext(Vname)
            output = os.path.join(Vdir, baseName + "_with_subtitles" + extention)
            
            stream = ffmpeg.input(path)
            subtitle_path = subtitle_file.replace('\\', '/').replace(':', '\\:')
            stream = ffmpeg.filter(stream, 'subtitles', subtitle_path)
            stream = ffmpeg.output(
                stream, 
                output, 
                vcodec='libx264',
                acodec='copy',
                preset='medium',
                crf=23
            )
            ffmpeg.run(stream, cmd=ffmpeg_executable, overwrite_output=True, quiet=True)
            typer.echo(f"✅ Video with subtitles saved as: {output}")
            return
        except Exception as e:
            typer.echo(f"❌ Error burning existing subtitles: {e}")
            return

    typer.echo("🔄 Creating subtitles and burning into video...")
    transcription(Apath, lang)
    typer.echo("✅ Video ready with subtitles!")

@app.command()
def summarize(ratio : int = typer.Option(6, "--ratio", "-r", help="How much the summary smaller than original text"),lang : str =typer.Option("auto" , "--lang","-l",help ="""language is auto the orginal for translate use ISO 639-1 language code
Language	Code
Abkhazian	ab
Afar	aa
Afrikaans	af
Albanian	sq
Amharic	am
Arabic	ar
Armenian	hy
Assamese	as
Aymara	ay
Azerbaijani	az
Bashkir	ba
Basque	eu
Bengali, Bangla	bn
Bhutani	dz
Bihari	bh
Bislama	bi
Breton	br
Bulgarian	bg
Burmese	my
Byelorussian	be
Cambodian	km
Catalan	ca
Chinese	zh
Corsican	co
Croatian	hr
Czech	cs
Danish	da
Dutch	nl
English, American	en
Esperanto	eo
Estonian	et
Faeroese	fo
Fiji	fj
Finnish	fi
French	fr
Frisian	fy
Gaelic (Scots Gaelic)	gd
Galician	gl
Georgian	ka
German	de
Greek	el
Greenlandic	kl
Guarani	gn
Gujarati	gu
Hausa	ha
Hebrew	iw
Hindi	hi
Hungarian	hu
Icelandic	is
Indonesian	in
Interlingua	ia
Interlingue	ie
Inupiak	ik
Irish	ga
Italian	it
Japanese	ja
Javanese	jw
Kannada	kn
Kashmiri	ks
Kazakh	kk
Kinyarwanda	rw
Kirghiz	ky
Kirundi	rn
Korean	ko
Kurdish	ku
Laothian	lo
Latin	la
Latvian, Lettish	lv
Lingala	ln
Lithuanian	lt
Macedonian	mk
Malagasy	mg
Malay	ms
Malayalam	ml
Maltese	mt
Maori	mi
Marathi	mr
Moldavian	mo
Mongolian	mn
Nauru	na
Nepali	ne
Norwegian	no
Occitan	oc
Oriya	or
Oromo, Afan	om
Pashto, Pushto	ps
Persian	fa
Polish	pl
Portuguese	pt
Punjabi	pa
Quechua	qu
Rhaeto-Romance	rm
Romanian	ro
Russian	ru
Samoan	sm
Sangro	sg
Sanskrit	sa
Serbian	sr
Serbo-Croatian	sh
Sesotho	st
Setswana	tn
Shona	sn
Sindhi	sd
Singhalese	si
Siswati	ss
Slovak	sk
Slovenian	sl
Somali	so
Spanish	es
Sudanese	su
Swahili	sw
Swedish	sv
Tagalog	tl
Tajik	tg
Tamil	ta
Tatar	tt
Tegulu	te
Thai	th
Tibetan	bo
Tigrinya	ti
Tonga	to
Tsonga	ts
Turkish	tr
Turkmen	tk
Twi	tw
Ukrainian	uk
Urdu	ur
Uzbek	uz
Vietnamese	vi
Volapuk	vo
Welsh	cy
Wolof	who
Xhosa	xh
Yiddish	ji
Yoruba	yo
Zulu	zu
""")):

    path, Vdir, Vname = get_video_info()
    if not path or not os.path.exists(path):
        typer.echo("Please set a video first using 'textStudy video <path>' or the video file doesn't exist")
        return
    
    Apath = os.path.splitext(path)[0] + ".wav"
    if not os.path.exists(Apath):
        typer.echo("start converting to audio......")
        Apath = video2audio(path , Vdir)
        if not Apath:
            return

    trpath = os.path.splitext(path)[0] + ".txt"
    if not os.path.exists(trpath):
        typer.echo("start transcribing......")
        transcription_result = audio2text(Apath, lang)
        if not transcription_result:
            return
    else:
        with open(trpath, "r", encoding="utf-8") as f:
            transcription_result = {"text": f.read()}

    typer.echo("start summarizing......")
    summary(transcription_result['text'] , ratio)

@app.command()
def explain(fileType: str = typer.Option(...,"-t","--type",help ="Output file markdown, LaTex, or pdf as you want, and will be saved in same your video directory"),onAPI:bool = typer.Option(False,"-o","--onAPI" ,help="Are you want work with API instead of locally?"),API:str=typer.Option(None,"-a","--api"),model:str=typer.Option(None,"-m","--model"), key:str=typer.Option(None,"-k","--key")):

    path, Vdir, Vname = get_video_info()
    if not path or not os.path.exists(path):
        typer.echo("Please set a video first using 'textStudy video <path>' or the video file doesn't exist")
        return
    usedType = fileType.lower()
    Apath = os.path.splitext(path)[0] + ".wav"
    if not os.path.exists(Apath):
        typer.echo("start converting to audio......")
        Apath = video2audio(path , Vdir)
        if not Apath:
            return

    trpath = os.path.splitext(path)[0] + ".txt"
    if not os.path.exists(trpath):
        typer.echo("start transcribing......")
        transcription_result = audio2text(Apath)
        if not transcription_result:
            return
    else:
        typer.echo("using existing transcription file......")
        with open(trpath, "r", encoding="utf-8") as f:
            transcription_result = {"text": f.read()}

    typer.echo("start paraphrasing......")
    paraphrase(transcription_result['text'], usedType,onAPI,API,model,key)
    
@app.command()
def questions(number :int= typer.Option(...,"-n","--number", help="number generated questions on the video"), style:str = typer.Option(...,"-s","--style",help = "style of questions from next: multiple choice, true/false, short answer, essay, fill in the blank"), file_type: str = typer.Option(...,"-t","--type",help ="Output file markdown, LaTex, or pdf as you want, and will be saved in same your video directory"),onAPI:bool = typer.Option(False,"-o","--tAPI" ,help="Are you want work with API instead of locally?"),API:str=typer.Option(None,"-a","--api"),model:str=typer.Option(None,"-m","--model"), key:str=typer.Option(None,"-k","--key")):

    path, vdir, vname = get_video_info()

    usedType = file_type.lower()
    if not path or not os.path.exists(path):
        typer.echo("Please set a video first using 'textStudy video <path>' or the video file doesn't exist")
        return
    
    Apath = os.path.splitext(path)[0] + ".wav"
    if not os.path.exists(Apath):
        typer.echo("start converting to audio......")
        Apath = video2audio(path , Vdir)
        if not Apath:
            return

    trpath = os.path.splitext(path)[0] + ".txt"
    if not os.path.exists(trpath):
        typer.echo("start transcribing......")
        transcription_result = audio2text(Apath)
        if not transcription_result:
            return
    else:
        typer.echo("using existing transcription file......")
        with open(trpath, "r", encoding="utf-8") as f:
            transcription_result = {"text": f.read()}

    typer.echo("start preparing questions......")
    questions(number, transcription_result['text'], usedType,style,onAPI,API,model,key)

main = app
if __name__ == '__main__' :
    app()
