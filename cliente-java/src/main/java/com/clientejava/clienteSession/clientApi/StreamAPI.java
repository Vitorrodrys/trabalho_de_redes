package com.clientejava.clienteSession.clientApi;

import java.io.IOException;

import com.clientejava.Channel.TCPChannel;

public class StreamAPI extends BaseAPI {

    public StreamAPI(TCPChannel tcpChannel) {
        super(tcpChannel);
    }

    public void requestAVideoPackage() throws IOException {
        tcpChannel.writeCommand("get_video_frame");
    }

    public void sendFeedback(int receivedPackages) throws IOException {
        tcpChannel.writeCommand("feedback", receivedPackages);
    }
}