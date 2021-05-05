# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request
import git
import os

app = Flask(__name__)
w_secret = os.getenv("GITHUB-SECRET")


@app.route('/update_server', methods=['POST'])
def webhook():
	if request.method != 'POST':
		return 'OK'
	else:
		abort_code = 418
		# Do initial validations on required headers
		if 'X-Github-Event' not in request.headers:
			abort(abort_code)
		if 'X-Github-Delivery' not in request.headers:
			abort(abort_code)
		if 'X-Hub-Signature' not in request.headers:
			abort(abort_code)
		if not request.is_json:
			abort(abort_code)
		if 'User-Agent' not in request.headers:
			abort(abort_code)
		ua = request.headers.get('User-Agent')
		if not ua.startswith('GitHub-Hookshot/'):
			abort(abort_code)

		event = request.headers.get('X-GitHub-Event')
		if event == "ping":
			return json.dumps({'msg': 'Hi!'})
		if event != "push":
			return json.dumps({'msg': "Wrong event type"})

		x_hub_signature = request.headers.get('X-Hub-Signature')
		# webhook content type should be application/json for request.data to have the payload
		# request.data is empty in case of x-www-form-urlencoded
		if not is_valid_signature(x_hub_signature, request.data, w_secret):
			print('Deploy signature failed: {sig}'.format(sig=x_hub_signature))
			abort(abort_code)

		payload = request.get_json()
		if payload is None:
			print('Deploy payload is empty: {payload}'.format(
				payload=payload))
			abort(abort_code)

		if payload['ref'] != 'refs/heads/master':
			return json.dumps({'msg': 'Not master; ignoring'})

		repo = git.Repo('/home/tomflo/actions_test')
		origin = repo.remotes.origin

		pull_info = origin.pull()

		if len(pull_info) == 0:
			return json.dumps({'msg': "Didn't pull any information from remote!"})
		if pull_info[0].flags > 128:
			return json.dumps({'msg': "Didn't pull any information from remote!"})

		commit_hash = pull_info[0].commit.hexsha
		build_commit = f'build_commit = "{commit_hash}"'
		print(f'{build_commit}')
		return 'Updated PythonAnywhere server to commit {commit}'.format(commit=commit_hash)

@app.route('/')
def hello_world():
	return 'Hello from Pipeline Academy 123!'




