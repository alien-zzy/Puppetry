using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEditor.Build.Content;
using UnityEngine;
using UnityEngine.InputSystem;
using Valve.VR;

public class Controller : MonoBehaviour
{
    public SteamVR_Action_Boolean move;
    public SteamVR_Input_Sources handType = SteamVR_Input_Sources.LeftHand;
    public Transform handTransform;
    public Transform headset;
    public Transform Center;
    public Transform Head;

    enum movingmode { target, whole };
    enum hand { left, right };
    enum button { tigger, on, off }
    private hand myhand = hand.left;
    private movingmode mymovingmode = movingmode.target;
    Vector3 head_current_position = Vector3.one;
    float current_distance_x = 0;
    float current_distance_y = 0;
    public float distance_x = 0;
    public float distance_y = 0;
    private button Movingbutton = button.off;
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
            handType = SteamVR_Input_Sources.RightHand;
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
        bool handmove = move.GetState(handType);
        //press button to move the puppet
        if (handmove && Movingbutton == button.off)
        {
            Movingbutton = button.tigger;
        }
        if (Movingbutton == button.tigger && myhand == hand.left)
        {
            mymovingmode = movingmode.whole;
            head_current_position = Head_position;
            current_distance_x = distance_x;
            current_distance_y = distance_y;
            Movingbutton = button.on;
        }
        if (Movingbutton == button.tigger && myhand == hand.right)
        {
            mymovingmode = movingmode.whole;
            head_current_position = Head_position;
            current_distance_x = distance_x;
            current_distance_y = distance_y;
            Movingbutton = button.on;
        }

        if (!handmove && Movingbutton == button.on)
        {
            Movingbutton = button.off;
        }

        if (Movingbutton == button.off)
        {
            mymovingmode = movingmode.target;
        }
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
                Debug.Log(current_distance_x - distance_x);
                Head_position.x = head_current_position.x + 10 * (current_distance_x - distance_x);
                Head_position.y = head_current_position.y + 10 * (current_distance_y - distance_y);
                Head.position = Head_position;
                break;
        }

    }
}
