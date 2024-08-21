
import session_handler.Listen_Connections;
import session_handler.core.Log;
import session_handler.core.Settings;

public class Main {

    public static void main(String[] args) {
        // Inicializa as configurações do servidor
        Settings.ServerSettings serverSettings = new Settings.ServerSettings();
        
        // Inicializa o logging
        Log.initLogging(serverSettings);

        // Inicia a escuta de conexões
        Listen_Connections.listenConnections();
    }
}