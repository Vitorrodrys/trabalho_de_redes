package com.clientejava.core;

import java.util.Optional;

public class Settings {

    public static class SettingsEnvironment {
        private String serverIp;
        private int serverPort;

        public SettingsEnvironment() {
            this.serverIp = Optional.ofNullable(System.getenv("SERVER_IP")).orElse("127.0.0.1");
            this.serverPort = Integer.parseInt(Optional.ofNullable(System.getenv("SERVER_PORT")).orElse("50000"));
        }

        public String getServerIp() {
            return serverIp;
        }

        public int getServerPort() {
            return serverPort;
        }
    }

    public static class SessionSettings {
        private float udpChannelTimeout;
        private int networkMtu;

        public SessionSettings() {
            this.udpChannelTimeout = Float.parseFloat(Optional.ofNullable(System.getenv("UDP_CHANNEL_TIMEOUT")).orElse("2"));
            this.networkMtu = Integer.parseInt(Optional.ofNullable(System.getenv("NETWORK_MTU")).orElse("1500"));
        }

        public float getUdpChannelTimeout() {
            return udpChannelTimeout;
        }

        public int getNetworkMtu() {
            return networkMtu;
        }
    }
}