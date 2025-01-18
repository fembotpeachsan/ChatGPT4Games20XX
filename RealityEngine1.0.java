import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;

/**
 * A very basic 2D game engine example using Java2D.
 * This does NOT load real Pokémon assets or connect to the server.
 */
public class GameEngine extends JFrame {

    private GamePanel gamePanel;
    private boolean running;
    private final int FPS = 60;       // Target Frames Per Second
    private final int FRAME_TIME = 1000 / FPS;

    public GameEngine() {
        setTitle("PokeMMO - Basic Game Engine");
        setSize(800, 600);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        // Create the main panel responsible for rendering
        gamePanel = new GamePanel();
        add(gamePanel);

        // Start the main loop
        running = true;
        startGameLoop();

        // Key listener to control our sprite, for demonstration
        addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                gamePanel.handleKeyPress(e.getKeyCode());
            }
        });
    }

    /**
     * The game loop: update + render at a fixed FPS.
     * Typically runs in a separate thread.
     */
    private void startGameLoop() {
        new Thread(() -> {
            while (running) {
                long startTime = System.currentTimeMillis();

                // 1. Update game logic
                gamePanel.update();

                // 2. Repaint the panel (calls paintComponent)
                gamePanel.repaint();

                // 3. Maintain consistent FPS
                long endTime = System.currentTimeMillis();
                long elapsed = endTime - startTime;
                long sleepTime = FRAME_TIME - elapsed;
                if (sleepTime > 0) {
                    try {
                        Thread.sleep(sleepTime);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }).start();
    }

    /**
     * Stop the game loop, if needed.
     */
    public void stopEngine() {
        running = false;
    }

    /**
     * Entry point if you want to run this directly.
     * In practice, you might call new GameEngine() after a successful login in your PokeMMO code.
     */
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            GameEngine engine = new GameEngine();
            engine.setVisible(true);
        });
    }

    // =========================================
    // Inner Class: GamePanel for Rendering
    // =========================================
    private class GamePanel extends JPanel {
        // A simple sprite to show on screen
        private Sprite player;

        public GamePanel() {
            setPreferredSize(new Dimension(800, 600));
            // Initialize a test sprite
            player = new Sprite(100, 100, 32, 32, Color.RED);
        }

        // Called automatically by Swing to draw the panel
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);

            // Clear background
            g.setColor(Color.BLACK);
            g.fillRect(0, 0, getWidth(), getHeight());

            // Draw the sprite
            player.draw(g);
        }

        /**
         * Update game logic (e.g., sprite movement, animations)
         */
        public void update() {
            player.update();
        }

        /**
         * Handle key events for moving the sprite.
         */
        public void handleKeyPress(int keyCode) {
            switch (keyCode) {
                case KeyEvent.VK_LEFT:
                    player.dx = -2;
                    break;
                case KeyEvent.VK_RIGHT:
                    player.dx = 2;
                    break;
                case KeyEvent.VK_UP:
                    player.dy = -2;
                    break;
                case KeyEvent.VK_DOWN:
                    player.dy = 2;
                    break;
                default:
                    break;
            }
        }
    }

    // =========================================
    // Inner Class: A Simple Sprite
    // =========================================
    private static class Sprite {
        public int x, y;       // current position
        public int width, height;
        public int dx, dy;     // velocity in x and y
        private Color color;

        public Sprite(int x, int y, int width, int height, Color color) {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
            this.color = color;
        }

        public void update() {
            // Move the sprite
            x += dx;
            y += dy;

            // Slow down after each move, so the sprite doesn't
            // keep sliding forever
            dx = 0;
            dy = 0;
        }

        public void draw(Graphics g) {
            g.setColor(color);
            g.fillRect(x, y, width, height);
        }
    }
}
