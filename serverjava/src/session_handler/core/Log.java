package session_handler.core;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Log {

    private static final Logger logger = Logger.getLogger(Log.class.getName());

    public static void initLogging(Settings.ServerSettings serverSettings) {
        // Obtém o nível de log a partir das configurações do servidor
        Level logLevel = getLogLevel(serverSettings.getLogLevel());

        // Configura o nível do logger principal
        Logger rootLogger = Logger.getLogger("");
        rootLogger.setLevel(logLevel);

        // Log inicial informando o nível de log configurado
        logger.log(logLevel, "Logging with log level {0} ({1})", new Object[]{serverSettings.getLogLevel(), logLevel.intValue()});
    }

    private static Level getLogLevel(Settings.LogLevelsEnum levelEnum) {
        // Converte o enum de nível de log para o nível correspondente em Java
        switch (levelEnum) {
            case CRITICAL:
            case FATAL:
                return Level.SEVERE;
            case ERROR:
                return Level.SEVERE;
            case WARN:
            case WARNING:
                return Level.WARNING;
            case INFO:
                return Level.INFO;
            case DEBUG:
                return Level.FINE;
            default:
                return Level.INFO;
        }
    }

    public void debug(String format, Object... args) {
        if (logger.isLoggable(Level.FINE)) {
            logger.log(Level.FINE, format, args);
        }
    }

    public void info(String format, Object... args) {
        if (logger.isLoggable(Level.INFO)) {
            logger.log(Level.INFO, format, args);
        }
    }

    public void error(String format, IOException e) {
        if (logger.isLoggable(Level.SEVERE)) {
            logger.log(Level.SEVERE, format, e);
        }
    }

    public static void severe(String string) {
        throw new UnsupportedOperationException("Unimplemented method 'severe'");
    }
}