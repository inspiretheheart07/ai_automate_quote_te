import json
import os
import random
from dotenv import load_dotenv
from ai_automate_quote.quotes.generator import QuoteGenerator
from ai_automate_quote.images.creator import TextImageGenerator
from ai_automate_quote.videos.creator import VideoCreator
from ai_automate_quote.download.drive import DriveManager
from ai_automate_quote.amazon.s3Manager import AmazonS3Manager
from ai_automate_quote.upload.youtube import YouTubeUploader
from ai_automate_quote.upload.facebook import FacebookUploader
from ai_automate_quote.upload.instagram import InstagramUploader
from ai_automate_quote.upload.threads_upload import ThreadsUploader


def load_environment_variables():
    """Load and return environment variables."""
    load_dotenv()  # Ensure environment variables are loaded from the .env file.
    print(os.getenv('GEMENI_KEY'))
    env_vars = {
        "GEMENI_KEY": os.getenv('GEMENI_KEY'),
        "GEMENI_MODEL": os.getenv('GEMENI_MODEL'),
        "ADJECTIVES": os.getenv('ADJECTIVES').split(','),
        "THEMES": os.getenv('THEMES').split(','),
        "LANGUAGE": os.getenv('LANGUAGE'),
        "S3_ACCESS_KEY": os.getenv('S3_ACCESS_KEY'),
        "S3_SECRETE_KEY": os.getenv('S3_SECRETE_KEY'),
        "S3_ZONE": os.getenv('S3_ZONE'),
        "S3_BUCKET": os.getenv('S3_BUCKET'),
        "FB_VERSION": os.getenv('FB_VERSION'),
        "FB_PAGE_ID": os.getenv('FB_PAGE_ID'),
        "FB_PAGE_TOKEN": os.getenv('FB_PAGE_TOKEN'),
        "INSTA_PAGE_TOKEN":os.getenv('INSTA_PAGE_TOKEN'),
        "INSTA_PAGE_ID": os.getenv('INSTA_PAGE_ID'),
        "THREADS_VERSION": os.getenv('THREADS_VERSION'),
        "S3_URL": os.getenv('S3_URL'),
        "THREADS_PAGE_ID": os.getenv('THREADS_PAGE_ID'),
        "THREADS_PAGE_TOKEN": os.getenv('THREADS_PAGE_TOKEN'),
        "YT_JSON": os.getenv('YT_JSON'),
        "DRIVE_LINK": os.getenv('DRIVE_LINK')
    }

    return env_vars


def download_files(music):
    """Download necessary files from Google Drive."""
    download = DriveManager(json.loads(os.getenv('YT_JSON')), [os.getenv('DRIVE_LINK')])
    download.build_drive_service()
    download.download_files([f"{music}.mp3", 'bg.png', 'font_te.ttf', 'output_image.png'])


def generate_quote(env_vars):
    """Generate a quote using the Quote Generator."""
    quote = QuoteGenerator(env_vars["GEMENI_KEY"], env_vars["GEMENI_MODEL"])
    quote.generateQuote(env_vars["ADJECTIVES"], env_vars["THEMES"], env_vars["LANGUAGE"])
    return quote


def create_image_and_video(music):
    """Create image and video based on the generated quote."""
    with open("quote_data.json", "r", encoding="utf-8") as quote_data:
        image = TextImageGenerator('bg.png', 'font_te.ttf', 'output_image.png')
        image.text_on_background(json.load(quote_data)['quote'])
        video = VideoCreator('output_image.png', f'{music}.mp3', output_video_path='output_video.mp4', duration=55)
        print((quote_data))
        video.create_video_with_music()


def upload_to_s3():
    """Upload the video to Amazon S3."""
    s3 = AmazonS3Manager(
        os.getenv('S3_ACCESS_KEY'),
        os.getenv('S3_SECRETE_KEY'),
        os.getenv('S3_ZONE'),
        os.getenv('S3_BUCKET')
    )
    url = s3.upload_file_to_s3('output_video.mp4', 'output_video_te.mp4')
    return url


def upload_to_platforms(quote_data):
    """Upload video to YouTube, Facebook, Instagram, and Threads."""
    # print(quote_data)
    # yt = YouTubeUploader().initialize_upload(
    #     'output_video.mp4',
    #     quote_data['title'],
    #     quote_data['description'],
    #     quote_data['tags'],
    #     22, False
    # )

    # fb = FacebookUploader(quote_data, os.getenv('FB_VERSION'), os.getenv('FB_PAGE_ID'), os.getenv('FB_PAGE_TOKEN'))
    # fb.initialize_upload_session('output_video.mp4')

    inst = InstagramUploader(quote_data, os.getenv('FB_VERSION'), os.getenv('INSTA_PAGE_ID'), os.getenv('INSTA_PAGE_TOKEN'))
    inst.post_reel(video_url='output_video.mp4')
    #
    # th = ThreadsUploader(
    #     quote_data,
    #     os.getenv('THREADS_VERSION'),
    #     os.getenv('S3_URL'),
    #     os.getenv('THREADS_PAGE_ID'),
    #     os.getenv('THREADS_PAGE_TOKEN')
    # )
    # th.threads_post()


def main():
        # music = random.randint(101, 113)
        # env_vars = load_environment_variables()
        # download_files(music)
        # generate_quote(env_vars)
        # create_image_and_video(music)
        # url = upload_to_s3()
        with open("quote_data.json", "r", encoding="utf-8") as quote_data_file:
            quote_data = json.load(quote_data_file)
            upload_to_platforms(quote_data)

if __name__ == "__main__":
    main()
