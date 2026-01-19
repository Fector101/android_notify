package org.wally.waller;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class CarouselReceiver extends BroadcastReceiver {

    private static final String TAG = "CarouselReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        Toast.makeText(context, "Action received: " + action, Toast.LENGTH_LONG).show();

        // Read port.txt from app path
        File portFile = new File(
        context.getFilesDir().getAbsolutePath() + "/app/port.txt"
        );
        if (!portFile.exists()) {
            Log.e(TAG, "port.txt not found! in python app");
            return;
        }

        int port = 5006; // default
        try (BufferedReader br = new BufferedReader(new FileReader(portFile))) {
            String line = br.readLine();
            if (line != null) port = Integer.parseInt(line.trim());
        } catch (Exception e) {
            Log.e(TAG, "Error reading port.txt from python service", e);
            return;
        }

        // Determine OSC message
        String oscAddress = "";
        String oscArg = "";
        if ("ACTION_STOP".equals(action)) {
            oscAddress = "/stop";
            oscArg = "hello1 frm java STOP";
        } else if ("ACTION_RESUME".equals(action)) {
            oscAddress = "/resume";
            oscArg = "hello frm java RESUME";
        } else if ("ACTION_PAUSE".equals(action)) {
            oscAddress = "/pause";
            oscArg = "hello frm java PAUSE";
        } else {
            Toast.makeText(context, "Unknown action: " + action, Toast.LENGTH_SHORT).show();
            Log.w(TAG, "Unknown action from python: " + action);
            return;
        }

        final int finalPort = port;
        final String finalAddress = oscAddress;
        final String finalArg = oscArg;

        new Thread(() -> {
            try {
                sendOscMessage("127.0.0.1", finalPort, finalAddress, finalArg);
                Log.d(TAG, "OSC message sent to python: " + finalAddress + " " + finalArg);
            } catch (Exception e) {
                Log.e(TAG, "Failed to send OSC message to python", e);
            }
        }).start();
    }

    private void sendOscMessage(String host, int port, String address, String arg) throws Exception {
        InetAddress serverAddr = InetAddress.getByName(host);
        DatagramSocket socket = new DatagramSocket();

        byte[] addrBytes = (address + "\0").getBytes("US-ASCII");
        // OSC messages are padded to 4 bytes, simple approach:
        int padding = 4 - (addrBytes.length % 4);
        byte[] paddedAddr = new byte[addrBytes.length + padding];
        System.arraycopy(addrBytes, 0, paddedAddr, 0, addrBytes.length);

        // Arguments
        String typeTag = ",s\0\0"; // string argument
        byte[] typeBytes = typeTag.getBytes("US-ASCII");

        byte[] argBytes = (arg + "\0").getBytes("US-ASCII");
        int argPadding = 4 - (argBytes.length % 4);
        byte[] paddedArg = new byte[argBytes.length + argPadding];
        System.arraycopy(argBytes, 0, paddedArg, 0, argBytes.length);

        // Combine all
        byte[] message = new byte[paddedAddr.length + typeBytes.length + paddedArg.length];
        System.arraycopy(paddedAddr, 0, message, 0, paddedAddr.length);
        System.arraycopy(typeBytes, 0, message, paddedAddr.length, typeBytes.length);
        System.arraycopy(paddedArg, 0, message, paddedAddr.length + typeBytes.length, paddedArg.length);

        DatagramPacket packet = new DatagramPacket(message, message.length, serverAddr, port);
        socket.send(packet);
        socket.close();
    }
}