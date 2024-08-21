package session_handler.apiSession;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.logging.Logger;
import session_handler.core.Settings;

public class WindowHandler {

    private static final Logger logger = Logger.getLogger(WindowHandler.class.getName());
    private double videoByterate;
    private int currentWindowSize;
    private double threshold;
    private int currentState;
    private final int clusterSize;

    private enum State {
        STATE_ZERO,
        STATE_ONE,
        STATE_TWO,
        STATE_THREE,
        STATE_FOUR
    }

    private final StateAction[] stateActions;
    private final StateTransition[] stateTransitions;

    public WindowHandler(String videoPath) throws IOException {
        // Initialize clusterSize
        this.clusterSize = Settings.SessionSettings.getClusterSize();

        // Initialize other parameters
        this.videoByterate = getVideoByterate(videoPath);
        this.currentWindowSize = (int) (videoByterate * 0.05);
        this.currentWindowSize -= (this.currentWindowSize % clusterSize);
        this.threshold = videoByterate;
        this.currentState = State.STATE_ZERO.ordinal();

        // Initialize state actions and transitions
        stateActions = new StateAction[]{
            this::duplicateWindowSize,
            this::startsToBegging,
            this::duplicateUntilThreshold,
            this::incrementSlowly,
            this::keepCurrentWindowSize
        };

        stateTransitions = new StateTransition[]{
            this::stateZeroTransitions,
            this::stateOneTransitions,
            this::stateTwoTransitions,
            this::stateThreeTransitions,
            this::stateFourTransitions
        };
    }

    private double getVideoByterate(String videoPath) throws IOException {
        File file = new File(videoPath);
        double duration = getVideoDurationWithFFmpeg(file);
        if (duration > 0) {
            double byterate = (double) file.length() / duration;
            logger.info(String.format("Byte rate calculated successfully: %f bytes per second", byterate));
            return byterate;
        } else {
            logger.severe("Unable to calculate video byte rate with FFmpeg.");
            throw new IOException("Unable to calculate video byte rate with FFmpeg.");
        }
    }

    private double getVideoDurationWithFFmpeg(File file) throws IOException {
        ProcessBuilder processBuilder = new ProcessBuilder("ffmpeg", "-i", file.getAbsolutePath());
        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();
        InputStream inputStream = process.getInputStream();

        try (java.util.Scanner scanner = new java.util.Scanner(inputStream).useDelimiter("\\A")) {
            String output = scanner.hasNext() ? scanner.next() : "";

            String durationLine = output.lines()
                .filter(line -> line.contains("Duration:"))
                .findFirst()
                .orElse("");

            String[] parts = durationLine.split("Duration:")[1].trim().split(",")[0].trim().split(":");
            if (parts.length == 3) {
                double hours = Double.parseDouble(parts[0]);
                double minutes = Double.parseDouble(parts[1]);
                double seconds = Double.parseDouble(parts[2].split("\\.")[0]); // Remove milliseconds
                double duration = hours * 3600 + minutes * 60 + seconds;
                return duration;
            } else {
                logger.severe("Unable to parse video duration from FFmpeg output.");
                throw new IOException("Unable to parse video duration from FFmpeg output.");
            }
        } catch (Exception e) {
            logger.severe("Error reading FFmpeg output.");
            throw new IOException("Error reading FFmpeg output.", e);
        }
    }

    private void duplicateWindowSize() {
        this.currentWindowSize *= 2;
    }

    private void startsToBegging() {
        this.threshold = this.currentWindowSize / 2.0;
        this.currentWindowSize = (int) (this.videoByterate * 0.05);
        this.currentWindowSize -= (this.currentWindowSize % clusterSize);
    }

    private void duplicateUntilThreshold() {
        if (this.currentWindowSize * 2 > this.threshold) {
            return;
        }
        this.currentWindowSize *= 2;
    }

    private void incrementSlowly() {
        int newWindowSize = this.currentWindowSize + clusterSize;
        if (newWindowSize >= this.threshold) {
            return;
        }
        this.currentWindowSize = newWindowSize;
    }

    private void keepCurrentWindowSize() {
        logger.info("Keeping the current window size");
    }

    private void stateZeroTransitions(boolean lossesOccurred) {
        if (this.currentWindowSize * 2 >= this.threshold) {
            this.currentState = State.STATE_THREE.ordinal();
        } else {
            this.currentState = lossesOccurred ? State.STATE_ONE.ordinal() : State.STATE_ZERO.ordinal();
        }
    }

    private void stateOneTransitions(boolean lossesOccurred) {
        this.currentState = lossesOccurred ? State.STATE_ONE.ordinal() : State.STATE_TWO.ordinal();
    }

    private void stateTwoTransitions(boolean lossesOccurred) {
        if (lossesOccurred) {
            this.currentState = State.STATE_ONE.ordinal();
        } else if (this.currentWindowSize * 2 >= this.threshold) {
            this.currentState = State.STATE_THREE.ordinal();
        } else {
            this.currentState = State.STATE_TWO.ordinal();
        }
    }

    private void stateThreeTransitions(boolean lossesOccurred) {
        if (lossesOccurred) {
            this.currentState = State.STATE_ONE.ordinal();
        } else if (this.currentWindowSize + clusterSize >= this.threshold) {
            this.currentState = State.STATE_FOUR.ordinal();
        } else {
            this.currentState = State.STATE_THREE.ordinal();
        }
    }

    private void stateFourTransitions(boolean lossesOccurred) {
        if (!lossesOccurred) {
            this.currentState = State.STATE_FOUR.ordinal();
        } else {
            this.currentState = State.STATE_ZERO.ordinal();
            this.threshold = this.videoByterate;
            this.currentWindowSize = (int) (this.videoByterate * 0.05);
            this.currentWindowSize -= (this.currentWindowSize % clusterSize);
        }
    }

    public void updateWindowSize(int byteCount) {
        boolean lossesOccurred = (byteCount / this.currentWindowSize) != 1;
        stateTransitions[this.currentState].transition(lossesOccurred);
        stateActions[this.currentState].action();
        logger.info(String.format("Update window size to %d", this.currentWindowSize));
        logger.info(String.format("Current state: %d", this.currentState));
    }

    public int getWindowSize() {
        assert this.currentWindowSize % clusterSize == 0;
        return this.currentWindowSize;
    }

    @FunctionalInterface
    private interface StateAction {
        void action();
    }

    @FunctionalInterface
    private interface StateTransition {
        void transition(boolean lossesOccurred);
    }
}