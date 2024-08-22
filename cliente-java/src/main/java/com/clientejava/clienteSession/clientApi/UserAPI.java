package com.clientejava.clienteSession.clientApi;
import java.io.IOException;

import com.clientejava.Channel.TCPChannel;

public class UserAPI extends BaseAPI {

    public UserAPI(TCPChannel tcpChannel) {
        super(tcpChannel);
    }

    public void seek(int offset) throws IOException {
        tcpChannel.writeCommand("seek", offset);
        if (tcpChannel.readData().equals("invalid seek position")) {
            throw new IllegalArgumentException("Invalid seek position");
        }
    }

    public void stop() throws IOException {
        tcpChannel.writeCommand("stop");
        if (!tcpChannel.readData().equals("ok")) {
            throw new AssertionError("Expected 'ok' response");
        }
        tcpChannel.close();
    }

    public void pause() throws IOException {
        tcpChannel.writeCommand("pause");
    }
}