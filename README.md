1. start a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```
2. install dependencies
```
pip install arxiv requests openai python-dotenv
```
3. set up a .env file
```
OPENAI_API_KEY=
EMAIL_ADDRESS=
EMAIL_PASSWORD=
RECIPIENT_EMAIL=
```
4. choose keywords and set max_results
5. run the script
6. papers will be saved locally to file system and summaries will be sent via email. enjoy!
