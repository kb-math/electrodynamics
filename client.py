from view.scene import *

import json
import requests
import time

class FrameFetcher(object):
	def __init__(self, base_url):
		self._base_url = base_url

	def request_frames(self, dt, duration):
		url = self._base_url

		url += "/trajectory"

		url += "?"
		url += "dt=" + str(dt)
		url += "&"
		url += "duration=" + str(duration)

		response = requests.get(url)

		return list(response.json())

if __name__ == '__main__':

	with open("config.json") as f:
		config = json.loads(f.read())
		base_url = config.get("base_url")

	frame_fetcher = FrameFetcher(base_url)
	plotting_engine = ContinuousPlotter(get_next_frames_callback = frame_fetcher.request_frames)

	frame_fetching_thread = threading.Thread(target = plotting_engine.fetch_continuously)

	rendering_thread = threading.Thread(target = plotting_engine.plot_continuously)

	frame_fetching_thread.daemon = True
	rendering_thread.daemon = True

	frame_fetching_thread.start()
	rendering_thread.start()

	while True:
		time.sleep(1.0)