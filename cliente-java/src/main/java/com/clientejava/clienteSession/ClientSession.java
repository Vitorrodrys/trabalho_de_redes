package com.clientejava.clienteSession;

import com.clientejava.Channel.TCPChannel;
import com.clientejava.Channel.UDPChannel;

import com.clientejava.clienteSession.clientApi.StreamAPI;
import com.clientejava.clienteSession.clientApi.UserAPI;

public class ClientSession {

    public static SessionData startsANewSession(String wishedVideo) throws Exception {
        UDPChannel udpChannel = new UDPChannel();
        TCPChannel tcpChannel = TCPChannel.createTcpChannel(wishedVideo, udpChannel.getListeningUdpPort());

        UserAPI userApi = new UserAPI(tcpChannel);
        StreamAPI streamApi = new StreamAPI(tcpChannel);
        StreamLayer streamLayer = new StreamLayer(streamApi, udpChannel);
        int videoSize = Integer.parseInt(tcpChannel.readData());

        return new SessionData(userApi, streamLayer, videoSize);
    }

    public static class SessionData {
        public final UserAPI userApi;
        public final StreamLayer streamLayer;
        public final int videoSize;

        public SessionData(UserAPI userApi, StreamLayer streamLayer, int videoSize) {
            this.userApi = userApi;
            this.streamLayer = streamLayer;
            this.videoSize = videoSize;
        }
    }
}