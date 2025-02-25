using UnityEngine;
using System.Net.Sockets;
using System.IO;

public class CoordinateSender : MonoBehaviour
{
    TcpClient client;
    StreamWriter writer;

    void Start()
    {
        client = new TcpClient("127.0.0.1", 12345);  // 连接到本地的 12345 端口
        writer = new StreamWriter(client.GetStream());
        writer.AutoFlush = true;
    }

    void Update()
    {
        Vector3 position = transform.position;
        writer.WriteLine($"{position.x},{position.y},{position.z}");
    }

    void OnDestroy()
    {
        writer.Close();
        client.Close();
    }
}