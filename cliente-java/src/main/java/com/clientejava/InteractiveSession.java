package com.clientejava;

import java.io.IOException;
import java.util.Scanner;

import com.clientejava.clienteSession.clientApi.UserAPI;
import com.clientejava.clienteSession.ClientSession;
import com.clientejava.clienteSession.StreamLayer;

public class InteractiveSession {

    private Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        InteractiveSession session = new InteractiveSession();
        session.interactiveCli();
    }

    public void interactiveCli() {
        UserSessionData userSessionData = startsUserSession();
        try {
            _interactiveCli(userSessionData.userApi, userSessionData.streamLayer, userSessionData.videoSize);
        } finally {
            try {
                userSessionData.userApi.stop();
            } catch (IOException e) {
                e.printStackTrace();
            }
            userSessionData.streamLayer.stop();
            System.out.println("Session closed");
        }
    }

    private UserSessionData startsUserSession() {
        while (true) {
            System.out.print("Video path: ");
            String videoPath = scanner.nextLine();
            try {
                ClientSession.SessionData sessionData = ClientSession.startsANewSession(videoPath);
                return new UserSessionData(sessionData.userApi, sessionData.streamLayer, sessionData.videoSize);
            } catch (Exception e) {
                System.out.println("Error to start session: " + e.getMessage());
            }
        }
    }

    private void interactiveSeek(UserAPI userApi, StreamLayer streamLayer, int videoSize) {
        System.out.print("Percentage video to seek: ");
        float percentageVideo = Float.parseFloat(scanner.nextLine()) / 100;
        int offset = (int) (videoSize * percentageVideo);
        try {
            streamLayer.getLock().lock();
            try {
                userApi.seek(offset);
            } finally {
                streamLayer.getLock().unlock();
            }
        } catch (IOException e) {
            System.err.println("An error occurred while seeking: " + e.getMessage());
        }
    }

    private void interactivePause(UserAPI userApi, StreamLayer streamLayer) {
        try {
            streamLayer.pause();
            userApi.pause();
        } catch (IOException e) {
            System.err.println("An error occurred while pausing: " + e.getMessage());
        }
    }

    private void _interactiveCli(UserAPI userApi, StreamLayer streamLayer, int videoSize) {
        String command;
        while (true) {
            System.out.print("Type a command: ");
            command = scanner.nextLine();
            switch (command) {
                case "pause":
                    interactivePause(userApi, streamLayer);
                    break;
                case "seek":
                    interactiveSeek(userApi, streamLayer, videoSize);
                    break;
                case "quit":
                    try {
                        userApi.stop();
                    } catch (IOException e) {
                        System.err.println("An error occurred while stopping: " + e.getMessage());
                    }
                    streamLayer.stop();
                    System.out.println("Session closed");
                    return;
                default:
                    System.out.println("Unknown command");
            }
        }
    }

    private static class UserSessionData {
        public final UserAPI userApi;
        public final StreamLayer streamLayer;
        public final int videoSize;

        public UserSessionData(UserAPI userApi, StreamLayer streamLayer, int videoSize) {
            this.userApi = userApi;
            this.streamLayer = streamLayer;
            this.videoSize = videoSize;
        }
    }
}