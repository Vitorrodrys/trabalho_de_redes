package session_handler.apiSession;

import java.io.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

import session_handler.Data_channel.UDPChannel;
import session_handler.core.Settings.SessionSettings;

public class StreamLayer {

    // Define the request frame class
    public static class RequestFrame {
        private final int size;

        public RequestFrame(int size) {
            this.size = size;
        }

        public int getSize() {
            return size;
        }
    }

    // WorkerStreamLayer as a private static inner class
    private static class WorkerStreamLayer {

        private final UDPChannel udpChannel;
        private final String videoPath;
        private final RandomAccessFile videoFile;
        private final long fileSize;
        private final BlockingQueue<RequestFrame> requestsQueue;
        private final ReentrantLock lock = new ReentrantLock();
        private final ReentrantLock pauseLock = new ReentrantLock();
        private final CountDownLatch killEvent = new CountDownLatch(1);
        private final Thread workerThread;

        private WorkerStreamLayer(UDPChannel udpChannel, String videoPath) throws IOException {
            this.udpChannel = udpChannel;
            this.videoPath = videoPath;
            this.videoFile = new RandomAccessFile(videoPath, "r");
            this.fileSize = videoFile.length();
            SessionSettings sessionSettings = new SessionSettings(); // Create an instance of SessionSettings
            this.requestsQueue = new LinkedBlockingQueue<>(sessionSettings.getMaxRequests());
            this.workerThread = new Thread(this::handlerVideo);
            this.workerThread.start();
        }

        private void processRequest(RequestFrame requestFrame) {
            lock.lock();
            try {
                byte[] data = new byte[requestFrame.getSize()];
                int bytesRead = videoFile.read(data);
                if (bytesRead > 0) {
                    udpChannel.sendData(data);
                }
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                lock.unlock();
            }
        }

        private void handlerVideo() {
            while (true) {
                try {
                    pauseLock.lock();
                    try {
                        if (killEvent.getCount() == 0) {
                            return;
                        }

                        RequestFrame requestFrame = requestsQueue.poll(1, TimeUnit.SECONDS);
                        if (requestFrame != null) {
                            processRequest(requestFrame);
                        }
                    } finally {
                        pauseLock.unlock();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }

        public void stop() throws IOException {
            lock.lock();
            try {
                videoFile.close();
            } finally {
                lock.unlock();
            }
            killEvent.countDown();
            try {
                workerThread.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            udpChannel.close();
        }
    }

    private final WorkerStreamLayer workerStreamLayer;

    public StreamLayer(UDPChannel udpChannel, String videoPath) throws IOException {
        this.workerStreamLayer = new WorkerStreamLayer(udpChannel, videoPath);
    }

    public void addRequest(RequestFrame requestFrame) {
        try {
            workerStreamLayer.requestsQueue.put(requestFrame);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public boolean updateOffset(long offset) {
        if (offset >= workerStreamLayer.fileSize) {
            return false;
        }
        workerStreamLayer.lock.lock();
        try {
            workerStreamLayer.videoFile.seek(offset);
            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        } finally {
            workerStreamLayer.lock.unlock();
        }
    }

    public void pause() {
        workerStreamLayer.pauseLock.lock();
    }

    public void stop() throws IOException {
        workerStreamLayer.stop();
    }

    @SuppressWarnings("removal")
    @Override
    protected void finalize() throws Throwable {
        try {
            stop();
        } finally {
            super.finalize();
        }
    }
}