package session_handler;

import java.io.File;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.List;

import session_handler.core.Settings.ServerSettings;
import session_handler.Data_channel.TCPChannel;
import session_handler.Data_channel.UDPChannel;
import session_handler.core.Log;
import session_handler.apiSession.SessionManager;

public class Listen_Connections {

    private static final ServerSettings serverSettings = new ServerSettings();
    private static final Log logger = new Log();

    public static void createSession(TCPChannel tcpChannel, String clientAddress) {
        try {
            List<String[]> response = tcpChannel.readDatas();
            if (response.isEmpty() || response.get(0).length < 2) {
                logger.error("Invalid response format", null);
                tcpChannel.writeData("error InvalidFormat");
                return;
            }

            String udpPort = response.get(0)[0];
            String videoPath = response.get(0)[1];

            logger.info(String.format("Starting a session with %s, streaming video %s to UDP port %s",
                    clientAddress, videoPath, udpPort));

            File videoFile = new File(videoPath);
            if (!videoFile.exists()) {
                tcpChannel.writeData("error NotFound");
                return;
            }

            UDPChannel udpChannel = new UDPChannel(clientAddress, Integer.parseInt(udpPort));
            tcpChannel.writeData(String.valueOf(videoFile.length()));

            SessionManager.startSession(tcpChannel, udpChannel, videoPath);

            logger.info(String.format("Session with client %s was closed", clientAddress));

        } catch (IOException e) {
            logger.error("Error in createSession", e);
        }
    }

    public static void listenConnections() {
        try {
            ServerSocket tcpSocket = TCPChannel.createTcpSocket(
                    serverSettings.getServerIp(), serverSettings.getServerPort(), null);

            logger.debug(String.format("Server listening on %s:%d",
                    serverSettings.getServerIp(), serverSettings.getServerPort()));

            while (true) {
                Socket clientSocket = tcpSocket.accept();
                String clientAddress = clientSocket.getInetAddress().getHostAddress();

                logger.debug(String.format("Connection from %s", clientAddress));

                TCPChannel tcpChannel = new TCPChannel(clientSocket);

                // Create a new thread for each session
                new Thread(() -> createSession(tcpChannel, clientAddress)).start();
            }

        } catch (IOException e) {
            logger.error("Error in listenConnections", e);
        }
    }

    public static void main(String[] args) {
        // Initialize logging with server settings
        Log.initLogging(serverSettings);

        listenConnections();
    }
}