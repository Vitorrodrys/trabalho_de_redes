package com.clientejava;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.*;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.logging.Logger;

import com.clientejava.core.Settings.SettingsEnvironment;
import com.clientejava.core.Settings.SessionSettings;

@SuppressWarnings("unused")
public class Channel {
    private static final Logger logger = Logger.getLogger(Channel.class.getName());

    private static final byte[] EOF = "#END#".getBytes();

    private static final SettingsEnvironment envSettings = new SettingsEnvironment();
    private static final SessionSettings sessionSettings = new SessionSettings();

    private static final int IP_HEADER_SIZE = 20;
    private static final int UDP_HEADER_SIZE = 8;
    private static final int PACKAGE_MTU = sessionSettings.getNetworkMtu() - IP_HEADER_SIZE - UDP_HEADER_SIZE;

    private static final int OFFSET_HEADER_SIZE = 4;
    private static final int DATA_LENGTH_HEADER_SIZE = 4;
    private static final int VIDEO_BYTES_SIZE = PACKAGE_MTU - OFFSET_HEADER_SIZE - DATA_LENGTH_HEADER_SIZE;

    public static abstract class BaseChannel {
        protected Socket socket;

        public BaseChannel(Socket socket) {
            this.socket = socket;
        }

        public void close() throws IOException {
            socket.close();
        }
    }

    public static class TCPChannel extends BaseChannel {
        public TCPChannel(Socket socket) {
            super(socket);
        }

        public static TCPChannel createTcpChannel(String videoPath, int udpPort) throws IOException {
            Socket tcpSocket = new Socket(envSettings.getServerIp(), envSettings.getServerPort());
            TCPChannel tcpChannel = new TCPChannel(tcpSocket);
            tcpChannel.writeData(udpPort + " " + videoPath);
            return tcpChannel;
        }

        public String readDatas() throws IOException {
            byte[] buffer = new byte[1024];
            int bytesRead = socket.getInputStream().read(buffer);
            return new String(buffer, 0, bytesRead, "UTF-8");
        }

        private void writeData(String data) throws IOException {
            byte[] dataBytes = data.getBytes("UTF-8");
            if (new String(dataBytes).contains(new String(EOF))) {
                throw new IllegalArgumentException("data contains EOF");
            }
            byte[] finalData = ByteBuffer.allocate(dataBytes.length + EOF.length + 2)
                                         .put(dataBytes)
                                         .put(" ".getBytes("UTF-8"))
                                         .put(EOF)
                                         .put(" ".getBytes("UTF-8"))
                                         .array();
            socket.getOutputStream().write(finalData);
        }

        public void writeCommand(Object... args) throws IOException {
            String data = String.join(" ", argsToStringArray(args));
            writeData(data);
        }

        private String[] argsToStringArray(Object... args) {
            String[] strArgs = new String[args.length];
            for (int i = 0; i < args.length; i++) {
                strArgs[i] = args[i].toString();
            }
            return strArgs;
        }
    }

    public static class UDPChannel {
        private DatagramSocket socket;

        public UDPChannel() throws SocketException {
            this.socket = new DatagramSocket();
            this.socket.setSoTimeout((int) sessionSettings.getUdpChannelTimeout() * 1000);
        }

        public int getListeningUdpPort() {
            return socket.getLocalPort();
        }

        private static class PackageData {
            public final int offset;
            public final byte[] data;

            public PackageData(int offset, byte[] data) {
                this.offset = offset;
                this.data = data;
            }
        }

        private PackageData deserialize(byte[] packageData) {
            ByteBuffer buffer = ByteBuffer.wrap(packageData);
            int offset = buffer.getInt();
            int dataLength = buffer.getInt();
            byte[] data = new byte[dataLength];
            buffer.get(data, 0, dataLength);
            return new PackageData(offset, data);
        }

        public byte[] receiveFrame() throws IOException {
            List<PackageData> frame = new ArrayList<>();
            byte[] buffer = new byte[PACKAGE_MTU];
            while (true) {
                try {
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    socket.receive(packet);
                    PackageData packageData = deserialize(packet.getData());
                    if (packageData.offset == -1) {
                        break;
                    }
                    frame.add(packageData);
                } catch (SocketTimeoutException e) {
                    logger.warning("A timeout occurred while waiting to receive a stream package");
                    break;
                }
            }
            frame.sort(Comparator.comparingInt(p -> p.offset));
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            for (PackageData packageData : frame) {
                outputStream.write(packageData.data);
            }
            return outputStream.toByteArray();
        }

        public void close() {
            if (socket != null && !socket.isClosed()) {
                socket.close();
            }
        }
    }
}