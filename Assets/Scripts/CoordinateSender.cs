using UnityEngine;
using System.Net.Sockets;
using System.IO;

public class CoordinateSender : MonoBehaviour
{
    TcpClient client;
    StreamWriter writer;
    public GameObject armOne;
    public GameObject armTwo;
    public GameObject Head;
    public Vector3 HeadInitialPosition;

    private int frameCount = 0;

    void Start()
    {
        client = new TcpClient("127.0.0.1", 12345);  // 连接到本地的 12345 端口
        writer = new StreamWriter(client.GetStream());
        writer.AutoFlush = true;
        HeadInitialPosition = Head.transform.position;
    }

    void Update()
    {
        frameCount++;

        if (frameCount >= 5)
        {
            float left_distance_x = armOne.GetComponent<Controller>().distance_x;
            float left_distance_y = armOne.GetComponent<Controller>().distance_y;
            float right_distance_x = armTwo.GetComponent<Controller>().distance_x;
            float right_distance_y = armTwo.GetComponent<Controller>().distance_y;
            Vector3 Headposition = Head.transform.position - HeadInitialPosition;
            Vector3 armOnePosition = armOne.transform.position;
            Vector3 armTwoPosition = armTwo.transform.position;
            armOnePosition.x = (Headposition.x + left_distance_x) * 300;
            armOnePosition.y = (Headposition.y - left_distance_y) * 300;
            armTwoPosition.x = (Headposition.x + right_distance_x + 0.18f) * 300;
            armTwoPosition.y = (Headposition.y - right_distance_y) * 300;
            Debug.Log($"Left:{armOnePosition.x},{armOnePosition.y}" +
                             $"Right:{armTwoPosition.x},{armTwoPosition.y}");
            // 只发送两个物体的坐标（6个值）
            writer.WriteLine($"{armOnePosition.z},{armOnePosition.x},{armOnePosition.y}," +
                             $"{armTwoPosition.z},{armTwoPosition.x},{armTwoPosition.y}");


            frameCount = 0;  // Reset the frame count
        }
    }

    void OnDestroy()
    {
        writer.Close();
        client.Close();
    }
}