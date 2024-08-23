package com.clientejava.clienteSession.clientApi;

import java.io.IOException;

import com.clientejava.Channel.TCPChannel;

public class UserAPI extends BaseAPI {

    public UserAPI(TCPChannel tcpChannel) {
        super(tcpChannel);
    }

    public void seek(int offset) throws IOException {
        tcpChannel.writeCommand("seek", offset);
        if (tcpChannel.readDatas().equals("invalid seek position")) {
            throw new IllegalArgumentException("invalid seek position");
        }
    }

    public void stop() throws IOException {
        tcpChannel.writeCommand("stop");
        if (!tcpChannel.readDatas().equals("ok")) {
            throw new AssertionError("Expected 'ok' response");
        }
        tcpChannel.close();
    }

    public void pause() throws IOException {
        tcpChannel.writeCommand("pause");
    }
}