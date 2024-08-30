package com.clientejava.clienteSession.clientApi;

import com.clientejava.Channel.TCPChannel;

public abstract class BaseAPI {
    protected TCPChannel tcpChannel;

    public BaseAPI(TCPChannel tcpChannel) {
        this.tcpChannel = tcpChannel;
    }
}