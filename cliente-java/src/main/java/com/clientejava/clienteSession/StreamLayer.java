package com.clientejava.clienteSession;

import com.clientejava.Channel.UDPChannel;
import com.clientejava.clienteSession.clientApi.StreamAPI;

import java.io.OutputStream;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.atomic.AtomicBoolean;

public class StreamLayer {
    private final StreamAPI streamApi;
    private final UDPChannel udpChannel;
    private final Thread workerThread;
    private final Lock lock;
    private final Lock pause;
    private final AtomicBoolean killEvent;

    public StreamLayer(StreamAPI streamApi, UDPChannel udpChannel) {
        this.streamApi = streamApi;
        this.udpChannel = udpChannel;
        this.lock = new ReentrantLock();
        this.pause = new ReentrantLock();
        this.killEvent = new AtomicBoolean(false);
        this.pause.lock(); // Starts paused
        this.workerThread = new Thread(this::workerMethod);
        this.workerThread.start();
    }

    private void workerMethod() {
        try (OutputStream mpvPipe = createMpvPipe()) {
            while (!killEvent.get()) {
                lock.lock();
                try {
                    pause.lock();
                    try {
                        streamApi.requestAVideoPackage();
                        byte[] videoPackage = udpChannel.receiveFrame();
                        streamApi.sendFeedback(videoPackage.length);
                        mpvPipe.write(videoPackage);
                    } finally {
                        pause.unlock();
                    }
                } finally {
                    lock.unlock();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private OutputStream createMpvPipe() throws Exception {
        String[] mpvCommand = {
            "mpv",
            "--no-cache",
            "--demuxer-thread=no",
            "--quiet",
            "--no-terminal",
            "--input-conf=/dev/null",
            "-"
        };
        Process mpvProcess = new ProcessBuilder(mpvCommand).start();
        return mpvProcess.getOutputStream();
    }

    public Lock getLock() {
        return lock;
    }

    public void pause() {
        if (pause.tryLock()) {
            pause.unlock();
        } else {
            pause.lock();
        }
    }

    public void stop() {
        killEvent.set(true);
        try {
            workerThread.join();
            udpChannel.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}