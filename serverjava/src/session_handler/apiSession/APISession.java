package session_handler.apiSession;

import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.function.BiConsumer;
import session_handler.Data_channel.TCPChannel;
import session_handler.core.Log;

public class APISession {

    private final TCPChannel tcpChannel;
    private final WindowHandler windowHandler;
    private final StreamLayer streamLayer;
    private final CommandRegistry commandRegistry;

    public APISession(String videoPath, TCPChannel tcpChannel, StreamLayer streamLayer, CommandRegistry commandRegistry) throws IOException {
        this.tcpChannel = tcpChannel;
        this.windowHandler = new WindowHandler(videoPath);
        this.streamLayer = streamLayer;
        this.commandRegistry = commandRegistry;

        // Register commands
        commandRegistry.registerCommand("get_video_frame", this::requestAVideoPackage);
        commandRegistry.registerCommand("feedback", this::receiveClientFeedback);
        commandRegistry.registerCommand("seek", this::seekVideo);
        commandRegistry.registerCommand("stop", this::stop);
        commandRegistry.registerCommand("pause", this::pause);
    }

    private void requestAVideoPackage(APISession session, Object... args) {
        int packageSize = windowHandler.getWindowSize();
        streamLayer.addRequest(new StreamLayer.RequestFrame(packageSize));
    }

    private void receiveClientFeedback(APISession session, Object... args) {
        if (args.length > 0 && args[0] instanceof String) {
            try {
                int byteCount = Integer.parseInt((String) args[0]);
                windowHandler.updateWindowSize(byteCount);
            } catch (NumberFormatException e) {
                Log.severe("Failed to parse byte count from feedback: " + e.getMessage());
                // Trate o erro de conversão ou informe o cliente
            }
        } else {
            Log.severe("Invalid feedback format or no feedback provided.");
            // Trate o caso de formato inválido ou falta de feedback
        }
    }

    private void seekVideo(APISession session, Object... args) {
        if (args.length > 0 && args[0] instanceof Integer) {
            int offset = (Integer) args[0];
            if (!streamLayer.updateOffset(offset)) {
                try {
                    tcpChannel.writeData("invalid seek position");
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            try {
                tcpChannel.writeData("ok");
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else {
            Log.severe("Invalid seek offset format or no offset provided.");
            // Trate o caso de formato inválido ou falta de offset
        }
    }

    private void stop(APISession session, Object... args) {
        try {
            streamLayer.stop();
            tcpChannel.writeData("ok");
        } catch (IOException e) {
            e.printStackTrace();
        }
        throw new StopSessionException();
    }

    private void pause(APISession session, Object... args) {
        streamLayer.pause();
    }

    private void runCommand(String[] command) {
        String commandName = command[0];
        Optional<BiConsumer<APISession, Object[]>> commandFunc = commandRegistry.getCommand(commandName);
        if (commandFunc.isEmpty()) {
            try {
                tcpChannel.writeData("command " + commandName + " not found");
            } catch (IOException e) {
                e.printStackTrace();
            }
            return;
        }
        // Remove the command name and pass the rest as arguments
        Object[] args = new Object[command.length - 1];
        System.arraycopy(command, 1, args, 0, args.length);
        commandFunc.get().accept(this, args);
    }

    public void waitCommands() {
        while (true) {
            try {
                List<String[]> commands = tcpChannel.readDatas();
                for (String[] command : commands) {
                    runCommand(command);
                }
            } catch (StopSessionException e) {
                return;
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    // Custom exception for stopping session
    public static class StopSessionException extends RuntimeException {
    }
}