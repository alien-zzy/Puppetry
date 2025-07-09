using UnityEngine;
using System.Net.Sockets;
using System.IO;
using System.Collections.Generic;
using System;
using System.Threading;
public class CoordinateSender : MonoBehaviour
{
    TcpClient client;
    StreamWriter writer;
    public GameObject armOne;
    public GameObject armTwo;
    public GameObject Head;
    public Vector3 HeadInitialPosition;

    private int frameCount = 0;

    [Serializable]
    public class FrameData
    {
        public float armOne_x;
        public float armOne_y;
        public float armOne_z;
        public float armTwo_x;
        public float armTwo_y;
        public float armTwo_z;
        public float Head_x;
        public float Head_y;
        public float Head_z;
    }

    [Serializable]
    public class FrameDataCollection
    {
        public List<FrameData> frames = new List<FrameData>();
    }

    private FrameDataCollection allFrames = new FrameDataCollection();

    void Start()
    {
        client = new TcpClient("127.0.0.1", 12345);  // 连接到本地的 12345 端口
        writer = new StreamWriter(client.GetStream());
        writer.AutoFlush = true;
        HeadInitialPosition = Head.transform.position;
        string folder = Path.Combine(Application.dataPath, "Json");
        string path = Path.Combine(folder, "coordinates.json");
        if (File.Exists(path))
        {
            File.Delete(path);
            Debug.Log("[CoordinateRecorderJson] Previous JSON file deleted.");
        }
    }

    void Update()
    {
        frameCount++;

        if (frameCount >= 5)
        {
            // Get controller distance from controller object
            float left_distance_x = armOne.GetComponent<Controller>().distance_x;
            float left_distance_y = armOne.GetComponent<Controller>().distance_y;
            float right_distance_x = armTwo.GetComponent<Controller>().distance_x;
            float right_distance_y = armTwo.GetComponent<Controller>().distance_y;

            Vector3 Headposition = Head.transform.position - HeadInitialPosition;
            Vector3 armOnePosition = armOne.transform.position;
            Vector3 armTwoPosition = armTwo.transform.position;

            armOnePosition.x = (Headposition.x + left_distance_x - 0.4f) * 100;
            armOnePosition.y = (Headposition.y - left_distance_y) * 150;
            armTwoPosition.x = (Headposition.x + right_distance_x + 0.4f) * 100;
            armTwoPosition.y = (Headposition.y - right_distance_y) * 150;
            Headposition.x = Headposition.x * 100;
            Headposition.y = Headposition.y * 150;

            Debug.Log($"Left:{armOnePosition.x},{armOnePosition.y}" +
                             $"Right:{armTwoPosition.x},{armTwoPosition.y}");
            // send coordinate
            writer.WriteLine($"{armOnePosition.z},{armOnePosition.x},{armOnePosition.y}," +
                             $"{armTwoPosition.z},{armTwoPosition.x},{armTwoPosition.y}," +
                             $"{Headposition.z},{Headposition.x},{Headposition.y}");

            FrameData frame = new FrameData
            {
                armOne_x = armOnePosition.z,
                armOne_y = armOnePosition.x,
                armOne_z = armOnePosition.y,
                armTwo_x = armTwoPosition.z,
                armTwo_y = armTwoPosition.x,
                armTwo_z = armTwoPosition.y,
                Head_x = Headposition.z,
                Head_y = Headposition.x,
                Head_z = Headposition.y

            };

            allFrames.frames.Add(frame);

            frameCount = 0;  // Reset the frame count
        }
    }

    void OnDestroy()
    {
        writer.Close();
        client.Close();
        string json = JsonUtility.ToJson(allFrames, true);
        string folder = Path.Combine(Application.dataPath, "Json");
        string path = Path.Combine(folder, "coordinates.json");
        File.WriteAllText(path, json);
        Debug.Log($"[CoordinateRecorderJson] Saved {allFrames.frames.Count} frames to: {path}");
    }
}