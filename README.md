# PECTrainer
PECTrainer is a python tool to train Periodic Error Correction (PEC) on Celestron telescope mounts.  It is similar to the earlier PECTool but with some additional features.  It works along with an autoguider to record and average multiple worm periods of the mount behavior to provide a reliable table of corrections to improve tracking.

## Caveats
- Only works with Celestron mounts and only those that support PEC
- Only works with computer connection through the handcontrol (not directly into the mount's USB port)
- Does not work when connecting to the mount through CPWI as the ASCOM driver
- Requires an autoguider (app or device) to track a star and make corrections

## Requirements
- Python 3.7+
- Most likely requires Windows currently

## Installation
- Execute `python -m pip install pectrainer` at a command line
- (If you are familiar with python environments you may create one specifically for `PECTrainer` or choose an existing one)

## Preparation for use
- Connect the computer to the mount through the handcontrol
- Start and align the mount using the handcontrol
- Make sure the mount is polar aligned carefully
- Prepare the autoguider so it is able to guide, but don't start guiding yet
- Use the handcontrol to find the PEC index (recommended at this point but can be done later)

## Performing the PEC training
- Use the command line to go to a directory where you want to run and stor PEC logs
- Start `pectrainer` at a command line by typing the command `pectrainer`
- Connect to the mount's ASCOM driver (probably `Celestron Telescope Driver`)
- Select the number of cycles to train (the average of all cycles will be loaded to the mount)
- Confirm the `Seek index` is checked.  If not, click the checkbox to have the mount move a bit in RA to find the index and return - hence the recommendation to do it immediately after aligning the mount
- Enable autoguiding with the guiding app or device
- Press `Start training` to begin the training
- While the cycle is recorded a blue dot moves across the graph.  When each cycle completes the graph for that cycle will be shown
- Each worm period will take a few minutes
- When complete, view the final averaged graph in black and, if it looks ok, click `Upload to mount`
- To start playback of the recorded PEC curve, press `Enable mount PEC playback`, or enable playback using the handcontrol
- You are now done and can exit

## Additional features
- You may download and view the current PEC curve in the mount using `Download from mount`
- A new `PEC_*.json` file is created in the current directory every time you press `Start training` and it is updated with data for each cycle as it comes in
- The stored `PEC*.json` files may be loaded and viewed later, and optionally uploaded to the mount
- You may press `Stop training` if the accumulated curves look good enough and upload the current average to the mount

## For best results
- Polar align the mount well, but no need for perfection.  Within a few arc-minutes is fine.
- Autoguide on a star high up but reasonably near the equator - within 20 degrees perhaps.  You want to be close to the equator so the star is moving across the sky quickly, and high up so the seeing is better
- Use a short guide period of 1 second or so if possible.  [MetaGuide](https://www.smallstarspot.com/) works well for this.  Each PEC measurement is a few seconds long, and for a mount such as the `CGX-L` the gearbox terms around 21 seconds long are in phase on each cycle.  This means the PEC table can capture and correct such fast terms, but only if the guide exposures are short enough and the guide corrections happen around once per second
- For best results record and average 6 or more cycles on a night with good seeing
- The [Celestron StarSense Autoguider](https://www.celestron.com/products/starsense-autoguider) should also work well for PEC training because it makes rapid guide corrections

## Notes
- Make sure your mount is Celestron and has support for PEC
- Behavior on SynScan mounts is unknown
- There are issues with knowing if PEC playback is currently enabled, so the state is not displayed.  Make sure the PEC playback is really happening by using the handcontrol
- For the first cycle the worm period is not known and the graph is drawn 500 seconds wide.  But once the first worm period is captured, the axis will show the correct scale
- Any drift in the PEC curves will be removed from the displayed plot and from the curve loaded to the mount, but the `PEC*.json` file will store the raw curves
