package session_handler;

import java.io.IOException;
import java.net.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import session_handler.core.Settings.ServerSettings;
import session_handler.core.Settings.SessionSettings;

public class Data_channel {

    private static final SessionSettings sessionSettings = new SessionSettings();
    private static final ServerSettings serverSettings = new ServerSettings();

    private static final byte[] EOF = "#END#".getBytes(StandardCharsets.UTF_8);

    private static final int IP_HEADER_SIZE = 20;
    private static final int UDP_HEADER_SIZE = 8;
    private static final int PACKAGE_MTU = sessionSettings.getNetworkMtu() - IP_HEADER_SIZE - UDP_HEADER_SIZE;

    private static final int OFFSET_HEADER_SIZE = 4;
    private static final int DATA_LENGTH_HEADER_SIZE = 4;
    private static final int VIDEO_BYTES_SIZE = PACKAGE_MTU - OFFSET_HEADER_SIZE - DATA_LENGTH_HEADER_SIZE;

    public static abstract class BaseChannel {
        protected DatagramSocket udpSocket;
        protected Socket tcpSocket;

        public BaseChannel(Socket tcpSocket) {
            this.tcpSocket = tcpSocket;
        }

        public BaseChannel(DatagramSocket udpSocket) {
            this.udpSocket = udpSocket;
        }

        public void close() throws IOException {
            if (tcpSocket != null) {
                tcpSocket.close();
            } else if (udpSocket != null) {
                udpSocket.close();
            }
        }
    }

    public static class TCPChannel extends BaseChannel {

        public TCPChannel(Socket tcpSocket) {
            super(tcpSocket);
        }

        public static ServerSocket createTcpSocket(String ipListen, int port, Integer maxConnections) throws IOException {
            if (maxConnections == null) {
                maxConnections = serverSettings.getMaxConnections();
            }
            ServerSocket serverSocket = new ServerSocket();
            serverSocket.bind(new InetSocketAddress(ipListen, port));
            serverSocket.setReceiveBufferSize(maxConnections);
            return serverSocket;
        }

        public List<String[]> readDatas() throws IOException {
            byte[] buffer = new byte[1024];
            int bytesRead = tcpSocket.getInputStream().read(buffer);
            String[] datas = new String(buffer, 0, bytesRead, StandardCharsets.UTF_8).split(" ");
            return parseDatas(datas);
        }

        private List<String[]> parseDatas(String[] datas) {
            List<String[]> result = new ArrayList<>();
            List<String> currentList = new ArrayList<>();
            for (String data : datas) {
                if (data.equals(new String(EOF, StandardCharsets.UTF_8))) {
                    result.add(currentList.toArray(new String[0]));
                    currentList.clear();
                } else {
                    currentList.add(data);
                }
            }
            return result;
        }

        public void writeData(String data) throws IOException {
            tcpSocket.getOutputStream().write(data.getBytes(StandardCharsets.UTF_8));
        }
    }

    public static class UDPChannel extends BaseChannel {
        private final String clientAddress;
        private final int clientPort;

        public UDPChannel(String clientAddress, int clientPort) throws SocketException {
            super(new DatagramSocket());
            this.clientAddress = clientAddress;
            this.clientPort = clientPort;
        }

        private static byte[] serializeBytes(byte[] videoPackage, int offset) {
            ByteBuffer buffer = ByteBuffer.allocate(VIDEO_BYTES_SIZE + OFFSET_HEADER_SIZE + DATA_LENGTH_HEADER_SIZE);
            buffer.putInt(offset);
            buffer.putInt(videoPackage.length);
            buffer.put(videoPackage);
            return buffer.array();
        }

        public void sendData(byte[] data) throws IOException {
            InetAddress address = InetAddress.getByName(clientAddress);
            for (int index = 0; index < data.length; index += VIDEO_BYTES_SIZE) {
                byte[] videoPackage = new byte[Math.min(VIDEO_BYTES_SIZE, data.length - index)];
                System.arraycopy(data, index, videoPackage, 0, videoPackage.length);
                byte[] packageBytes = serializeBytes(videoPackage, index);
                udpSocket.send(new DatagramPacket(packageBytes, packageBytes.length, address, clientPort));
            }
            byte[] eofPackage = serializeBytes(new byte[]{-1}, -1);
            udpSocket.send(new DatagramPacket(eofPackage, eofPackage.length, address, clientPort));
        }
    }
}