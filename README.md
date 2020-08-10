# ankiplay - Use your own audio player for playback in Anki

A custom audio queue for Anki versions lower than 2.1.17 and a Bash script which plays audio files while normalizing them in real-time.
When combined, they offer a much more pleasant reviewing experience and generally give you maximum control over how audio is played back inside Anki.

## Requirements

The Bash script is primarily developed for running on Debian Buster.
It will probably also run fine on most other modern Linux distributions, but please keep in mind that it was not tested with a wide variety of them.
It needs ffmpeg and aplay installed on the system.

The Anki addon will—as stated above—only work on Anki versions lower than 2.1.17.
This is because in Anki 2.1.17 (and again in Anki 2.1.20), the audio system has been completely reworked.
Feel free to submit a pull request for an alternative addon file that works in Anki versions 2.1.20 and later!
I am currently on Debian Buster, so I am personally fine for now.

## Usage

Install your desired audio player and find out the path to its executable through whereis or place the Bash script `ankiplay` somewhere in your system.
Make sure that it is executable.
Edit the script's behavior if you like!
Mine contains some really specific suff depending on the naming scheme of the audio file.
In the end, it is all just there to build the filter string for ffmpeg that will alter the audio in real-time.

Go to your Anki addons folder inside your Anki profile, create a new folder named "ankiplay" (or so) and copy the `__init__.py` into it.
Open it in a text editor, navigate to the function `ankiplay_play` and set the path of your custom audio player (for me, it is `"/opt/ankiPlay"`) in the call to `subprocess.Popen`.
Make sure that the newly copied `__init__.py` is executable.
After restarting Anki, all audio should now play through your own, customized audio player.

## Important

I developed this code to make Anki the way I personally wanted.
I cannot guarantee that you will be equally satisfied with the result.
Please consider creating an issue or a pull request if you know how to do it better.
If my contribution eased your language learning experience or you want me to help you with a specific problem more quickly, consider [donating as much as you feel I deserve](https://www.paypal.me/jojosoft/5)!
