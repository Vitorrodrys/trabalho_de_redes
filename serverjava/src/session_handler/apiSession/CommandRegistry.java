package session_handler.apiSession;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.BiConsumer;

public class CommandRegistry {

    private final Map<String, BiConsumer<APISession, Object[]>> commandMap = new HashMap<>();

    /**
     * Registers a command with a given name and associated function.
     * @param commandName The name of the command to register.
     * @param command The function to execute when the command is invoked.
     */
    public void registerCommand(String commandName, BiConsumer<APISession, Object[]> command) {
        if (commandMap.containsKey(commandName)) {
            throw new IllegalArgumentException("Command '" + commandName + "' is already registered.");
        }
        commandMap.put(commandName, command);
    }

    /**
     * Executes the command associated with the given name.
     * @param commandName The name of the command to execute.
     * @param session The APISession to pass to the command function.
     * @param args Arguments to pass to the command function.
     */
    public void executeCommand(String commandName, APISession session, Object... args) {
        BiConsumer<APISession, Object[]> command = commandMap.get(commandName);
        if (command == null) {
            throw new IllegalArgumentException("Command '" + commandName + "' not found.");
        }
        command.accept(session, args);
    }

    /**
     * Retrieves the command function associated with the given name.
     * @param commandName The name of the command.
     * @return An Optional containing the command function, or an empty Optional if not found.
     */
    public Optional<BiConsumer<APISession, Object[]>> getCommand(String commandName) {
        return Optional.ofNullable(commandMap.get(commandName));
    }
}