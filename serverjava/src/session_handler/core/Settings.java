package session_handler.core;
import java.util.Optional;

public class Settings {

    // Enum para os níveis de log
    public enum LogLevelsEnum {
        CRITICAL, FATAL, ERROR, WARN, WARNING, INFO, DEBUG
    }

    public static class ServerSettings {
        // Server settings
        private String serverIp;
        private int serverPort;
        private int maxConnections;
        private LogLevelsEnum logLevel;

        public ServerSettings() {
            this.serverIp = Optional.ofNullable(System.getenv("SERVER_IP")).orElse("127.0.0.1");
            this.serverPort = Integer.parseInt(Optional.ofNullable(System.getenv("SERVER_PORT")).orElse("50000"));
            this.maxConnections = Integer.parseInt(Optional.ofNullable(System.getenv("MAX_CONNECTIONS")).orElse("10"));
            this.logLevel = LogLevelsEnum.valueOf(Optional.ofNullable(System.getenv("LOG_LEVEL")).orElse("INFO"));
        }

        // Getters 
        public String getServerIp() {
            return serverIp;
        }

        public int getServerPort() {
            return serverPort;
        }

        public int getMaxConnections() {
            return maxConnections;
        }

        public LogLevelsEnum getLogLevel() {
            return logLevel;
        }

        @Override
        public String toString() {
            return "ServerSettings [serverIp=" + serverIp + ", serverPort=" + serverPort + ", maxConnections="
                    + maxConnections + ", logLevel=" + logLevel + "]";
        }

        
    }

    public static class SessionSettings {
        // Session settings
        private static int clusterSize;
        private int maxRequests;
        private int networkMtu;

        public SessionSettings() {
            SessionSettings.clusterSize = Integer.parseInt(Optional.ofNullable(System.getenv("CLUSTER_SIZE")).orElse("4096"));
            this.maxRequests = Integer.parseInt(Optional.ofNullable(System.getenv("MAX_REQUESTS")).orElse("10"));
            this.networkMtu = Integer.parseInt(Optional.ofNullable(System.getenv("NETWORK_MTU")).orElse("1500"));
        }

        // Getters
        public static int getClusterSize() {
            return clusterSize;
        }

        public  int getMaxRequests() {
            return maxRequests;
        }

        public int getNetworkMtu() {
            return networkMtu;
        }
    }
}
