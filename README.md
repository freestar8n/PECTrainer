# PECTrainer
`PECTrainer` is a python tool to train Periodic Error Correction (PEC) on Celestron telescope mounts.  It is similar to the earlier PECTool but with some additional features.  It works together with an autoguider to record and average multiple worm cycles of the mount behavior to provide a reliable table of corrections to improve tracking.

![Sample view](https://www.dropbox.com/s/gcejvwrzxgkxq34/PECTrainerView.png?raw=1)

## Caveats
- Only works with Celestron mounts and only those that support PEC
- Only works with computer connection through the handcontrol (not directly into the mount's USB port)
- Does not work when connecting to the mount through CPWI as the ASCOM driver
- Requires an autoguider (app, device, or human making corrections) to guide on a star

## Requirements
- Python 3.7+
- Most likely requires Windows currently

## Installation
- Execute `python -m pip install pectrainer` at a command line
- (If you are familiar with python environments you may create one specifically for `PECTrainer` or choose an existing one)

## Preparation for use
- Connect the computer to the mount through the handcontrol
- Start and align the mount using the handcontrol
- Make sure the mount is polar aligned to within a few arc-minutes (nothing crazy)
- Prepare the autoguider so it is able to guide, but don't start guiding yet
- Use the handcontrol to find the PEC index (recommended at this point but can be done later)

## Performing the PEC training
- Use the command line to go to a directory where you want to run and store PEC logs
- Start `pectrainer` at a command line by typing the command `pectrainer`
- Connect to the mount's ASCOM driver (probably `Celestron Telescope Driver`)
- Select the number of cycles to train (the average of all cycles will be automatically loaded to the mount when the cycles complete)
- Confirm the `Seek index` is checked.  If not, click the checkbox to have the mount move a bit in RA to find the index and approximately return - hence the recommendation to do it immediately after aligning the mount
- Choose a star to guide on and enable autoguiding with the guiding app or device (or manually guide with either the handcontrol or the ASCOM slew controls set to 0.5x sidereal rate)
- Press `Start training` to begin the training
- While the first cycle is recorded no graph will be shown but the progress gauge will begin to increase
- At the end of each cycle the graph will be updated with all previous curves, plus the current average in black
- Each worm period will take a few minutes - with time dependent on the type of mount
- When complete the average curve will automatically be uploaded to the mount
- To start playback of the recorded PEC curve, press `Enable mount PEC playback`, or enable playback using the handcontrol
- You are now done and can exit
- The PEC graph may be displayed either as a normal PE curve in arc-sec, or as a changing rate over time in arc-sec/s.  Here is a view as rate.  Note that the gearbox term shows clearly as a sinusoid with approximately 21 second period.  Other mounts will show different periods

![View of PE curve as rate](https://www.dropbox.com/s/ybo1dvb07nixf1b/PECTrainerRateView.png?raw=1)

## Additional features
- You may download and view the current PEC curve in the mount using `Download from mount`
- A new `PEC_*.json` file is created in the current directory every time you press `Start training` and it is updated with data for each cycle as it comes in
- The stored `PEC*.json` files may be loaded and viewed later, and optionally uploaded to the mount
- You may press `Stop training` if the accumulated curves look good enough and press `Upload` to manually load the current average to the mount

## For best results
- Polar align the mount well, but no need for perfection.  Within a few arc-minutes is fine.
- Autoguide on a star high up but reasonably near the equator - within 20 degrees perhaps.  You want to be close to the equator so the star is moving across the sky quickly, and high up so the seeing is better.
- Use a short guide period of 1 second or so if possible.  [MetaGuide](https://www.smallstarspot.com/) works well for this.  Each PEC measurement is a few seconds long, and for a mount such as the `CGX-L` the main belt or gear term is around 21 seconds long is in phase on each cycle.  This means the PEC table can capture and correct such fast terms, but only if the guide exposures are short enough and the guide corrections happen around once per second.
- For best results record and average 6 or more cycles on a night with good seeing.
- The [Celestron StarSense Autoguider](https://www.celestron.com/products/starsense-autoguider) should also work well for PEC training because it makes rapid guide corrections.
- If the mount has belt or gear terms that have the same phase on each cycle, they will stack on top of each other and show clearly in the average.  This is good and it means the PEC can smooth out the term.
- ... But in contrast, if the term is not in phase it will be different in each cycle and they won't stack in the average.  This means you should average many cycles so that the terms average out.  The PEC won't be able to smooth out the term - but at the same time the PEC curve won't have a residual gear term that would make tracking worse.

## Notes
- Make sure your mount is Celestron and has support for PEC
- Behavior on SynScan mounts is unknown, but it may work
- Once the mount is trained you can use the mount normally and you don't need to connect through the handcontrol.  You can also remove the handcontrol and use a different alignment app such as CPWI
- There are issues with knowing if PEC playback is currently enabled, so the state is not displayed in the GUI.  When done with training, make sure the PEC playback is really happening by enabling it with the handcontrol or CPWI
- Any drift in the PEC curves will be removed from the displayed plot and from the curve loaded to the mount
- Declination guide corrections have no impact on the recorded curve
- Some mounts don't guide well when PEC playback is enabled, but for Celestron mounts it can greatly improve guiding - particularly if the belt or gear term is smoothed out
