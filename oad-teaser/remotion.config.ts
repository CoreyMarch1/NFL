import {Config} from '@remotion/cli/config';

// Everything the composition loads lives in assets/ (videos, images, fonts).
Config.setPublicDir('assets');
Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('swangle');
if (process.env.CHROME_PATH) {
  Config.setBrowserExecutable(process.env.CHROME_PATH);
}
