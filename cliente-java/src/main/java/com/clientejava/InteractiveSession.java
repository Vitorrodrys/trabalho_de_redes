package com.clientejava;

import java.io.IOException;
import java.util.Scanner;

import com.clientejava.clienteSession.clientApi.UserAPI;
import com.clientejava.clienteSession.ClientSession;
import com.clientejava.clienteSession.StreamLayer;

public class InteractiveSession {

    private Scanner scanner = new Scanner(System.in);  // Mover Scanner para o nível de classe

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
        try (Scanner scanner = new Scanner(System.in)) {
            while (true) {
                System.out.print("Video path: ");
                String videoPath = scanner.nextLine();
                try {
                    ClientSession.SessionData sessionData = ClientSession.startsANewSession(videoPath);
                    // Acessando diretamente os membros públicos de SessionData
                    return new UserSessionData(sessionData.userApi, sessionData.streamLayer, sessionData.videoSize);
                } catch (Exception e) {
                    System.out.println("Error to start session" + e);
                }
            }
        }
    }
    

    private void interactiveSeek(UserAPI userApi, StreamLayer streamLayer, int videoSize) {
        System.out.print("Percentage video to seek: ");
        float percentageVideo = Float.parseFloat(scanner.nextLine()) / 100;
        int offset = (int) (videoSize * percentageVideo);
        try {
            streamLayer.getLock().lock();
            userApi.seek(offset);
        } catch (IOException e) {
            System.err.println("An error occurred while seeking: " + e.getMessage());
            e.printStackTrace();
        } finally {
            streamLayer.getLock().unlock();
        }
    }

    private void interactivePause(UserAPI userApi, StreamLayer streamLayer) {
        try {
            streamLayer.pause();
            userApi.pause();
        } catch (IOException e) {
            System.err.println("An error occurred while pausing: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void _interactiveCli(UserAPI userApi, StreamLayer streamLayer, int videoSize) {
        String command;

        while (true) {
            System.out.print("Type a command: ");
            command = scanner.nextLine();

            try {
                switch (command) {
                    case "pause":
                        interactivePause(userApi, streamLayer);
                        break;
                    case "seek":
                        interactiveSeek(userApi, streamLayer, videoSize);
                        break;
                    case "quit":
                        userApi.stop();
                        streamLayer.stop();
                        System.out.println("Session closed");
                        return;
                    default:
                        System.out.println("Unknown command");
                }
            } catch (IOException e) {
                System.err.println("An error occurred: " + e.getMessage());
                e.printStackTrace();
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