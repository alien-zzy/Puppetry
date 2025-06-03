using UnityEngine;
using System.Net.Sockets;
using System.IO;

public class CoordinateSender : MonoBehaviour
{
    TcpClient client;
    StreamWriter writer;
    public GameObject armOne;
    public GameObject armTwo;

    private int frameCount = 0;

    void Start()
    {
        client = new TcpClient("127.0.0.1", 12345);  // 连接到本地的 12345 端口
        writer = new StreamWriter(client.GetStream());
        writer.AutoFlush = true;
    }

    void Update()
    {
        frameCount++;

        if (frameCount >= 10)
        {
            Vector3 armOnePosition = armOne.transform.position;
            Vector3 armTwoPosition = armTwo.transform.position;

            // 只发送两个物体的坐标（6个值）
            writer.WriteLine($"{armOnePosition.x},{armOnePosition.y},{armOnePosition.z}," +
                             $"{armTwoPosition.x},{armTwoPosition.y},{armTwoPosition.z}");
            frameCount = 0;  // Reset the frame count
        }
    }

    void OnDestroy()
    {
        writer.Close();
        client.Close();
    }
}