from locale import setlocale, LC_NUMERIC
from anki import sound, hooks
import threading, queue
import subprocess
import signal
from aqt import mw
import os

ankiplay_enable_log = False

ankiplay_q = None
ankiplay_proc = None
ankiplay_last_path = ""


def ankiplay_init():
	global ankiplay_q
	setlocale(LC_NUMERIC, "C")
	ankiplay_q = queue.Queue()
	threading.Thread(target=ankiplay_player, daemon=True).start()
	ankiplay_log("Started playback thread.")


def ankiplay_player():
	while True:
		clear = False
		end = False
		command = ankiplay_q.get()
		if command == "END":
			clear = True
			end = True
		else:
			ankiplay_log(f'Play back file: {command}')
			if ankiplay_play(command) != 0:
				# The playback was intentionally aborted.
				# Clear the rest of the queue.
				clear = True
		if clear:
			# Ignore all remaining elements in the queue.
			# (Except for the "END" command, of course!)
			ankiplay_log("Clearing playback queue.")
			while not ankiplay_q.empty():
				try:
					if ankiplay_q.get(False) == "END":
						end = True
					ankiplay_q.task_done()
				except Empty:
					break
		if end:
			ankiplay_log("Stopping playback thread.")
			ankiplay_q.task_done()
			break
		ankiplay_log("Playback ended.")
		ankiplay_q.task_done()


def ankiplay_play(path):
	# Wait on the audio to be fully played back, but make the process global.
	# This can be used by other functions to stop the current playback.
	# (Otherwise, there would be no way to stop playback earlier...)
	global ankiplay_proc
	# Process vs. process group?!
	# Explanation: https://pymotw.com/2/subprocess/#process-groups-sessions
	# Also, without stdin = subprocess.PIPE, some weird effects happen.
	# Example: Terminals are rendered unusable after executing "anki" in them.
	# Typed characters do not show up anymore and output repeats itself...
	ankiplay_proc = subprocess.Popen(['/opt/ankiPlay', path], stdin = subprocess.PIPE, preexec_fn = os.setsid)
	ankiplay_proc.wait()
	rc = ankiplay_proc.returncode
	ankiplay_proc = None
	return rc


def ankiplay_queue(path):
	if ankiplay_q is None:
		ankiplay_init()

	global ankiplay_last_path
	# It seems that the path is not already absolute..?
	full_path = os.path.join(mw.col.media.dir(), path)
	# Only queue the path if it is different from the last one.
	# This is to avoid suckage when accidentally clicking twice.
	# (But allow replays of the last path if nothing plays back.)
	idle = ankiplay_q.empty() and ankiplay_proc is None
	if idle or full_path != ankiplay_last_path:
		ankiplay_q.put(full_path)
		ankiplay_last_path = full_path
		ankiplay_log(f'Queued file: {path}.')
	else:
		ankiplay_log(f'Skipped already queued file: {path}.')


def ankiplay_stop():
	if ankiplay_proc is None:
		return

	# See ankiplay_play for explanation...
	ankiplay_log("Stop playback.")
	os.killpg(ankiplay_proc.pid, signal.SIGINT)


def ankiplay_kill(*args):
	global ankiplay_q

	if ankiplay_q is None:
		return

	ankiplay_q.put("END")
	ankiplay_stop()
	ankiplay_q.join()
	ankiplay_q = None


def ankiplay_log(text):
	if ankiplay_enable_log:
		print("[ankiplay] " + text)


hooks.remHook("unloadProfile", sound.stopMplayer)
hooks.addHook("unloadProfile", ankiplay_kill)

sound._player = ankiplay_queue
sound._queueEraser = ankiplay_stop
