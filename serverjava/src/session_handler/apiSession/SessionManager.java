package session_handler.apiSession;

import java.io.IOException;

import session_handler.Data_channel.TCPChannel;
import session_handler.Data_channel.UDPChannel;

public class SessionManager {

    public static void startSession(TCPChannel tcpChannel, UDPChannel udpChannel, String videoPath) throws IOException {
        // Cria a instância do StreamLayer
        StreamLayer streamLayer = new StreamLayer(udpChannel, videoPath);
        
        // Cria a instância do APISession
        APISession apiSession = new APISession(videoPath, tcpChannel, streamLayer, new CommandRegistry());
        
        // Aguarda os comandos e processa a sessão
        apiSession.waitCommands();
    }
}