using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEditor.Build.Content;
using UnityEngine;
using UnityEngine.InputSystem;

public class Controller : MonoBehaviour
{
    public Transform handTransform;
    public Transform headset;
    public Transform Center;
    public Transform Head;

    enum movingmode { target, whole };
    enum hand { left, right };
    private hand myhand = hand.left;
    private movingmode mymovingmode = movingmode.target;
    Vector3 head_current_position = Vector3.one;
    float current_distance_x = 0;
    float current_distance_y = 0;
    public float distance_x = 0;
    public float distance_y = 0;
    //distance_x max: 0.78 min 0.16
    //distance_y 
    //target_y max 8.6 min 6.6
    //target_x min -48 min -45

    private void Start()
    {
        if (gameObject.name == "Target_right_hand")
        {
            //this is right hand controller;
            myhand = hand.right;
        }
    }

    // Update is called once per frame
    void Update()
    {
        Vector3 myposition = transform.position;
        Vector3 Head_position = Head.position;
        Vector3 centerposition = Center.position;

        distance_x = headset.position.x - handTransform.position.x;
        distance_y = headset.position.y - handTransform.position.y;

        //press button to move the puppet
        if (Input.GetKeyDown(KeyCode.A) && myhand == hand.left)
        {
            mymovingmode = movingmode.whole;
            head_current_position = Head_position;
            current_distance_x = distance_x;
            current_distance_y = distance_y;
        }
        if (Input.GetKeyDown(KeyCode.B) && myhand == hand.right)
        {
            mymovingmode = movingmode.whole;
            head_current_position = Head_position;
            current_distance_x = distance_x;
            current_distance_y = distance_y;
        }
        if (Input.GetKeyDown(KeyCode.Space))
        {
            mymovingmode = movingmode.target;
        }
        Debug.Log(distance_x);
        switch (mymovingmode)
        {
            case movingmode.target:
                //move target
                myposition.x = centerposition.x - 2.4f * distance_x;
                myposition.y = centerposition.y - 0.8f * distance_y;
                myposition.z = centerposition.z;
                transform.position = myposition;
                break;
            case movingmode.whole:
                //move whole body
                Head_position.x = head_current_position.x + 10 * (current_distance_x - distance_x);
                Head_position.y = head_current_position.y + 10 * (current_distance_y - distance_y);
                Head.position = Head_position;
                break;
        }

    }
}
