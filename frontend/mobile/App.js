import React,{useEffect,useState} from "react";
import {SafeAreaView,View,Text,TextInput,Button,ScrollView,StyleSheet,Alert} from "react-native";
const API=process.env.EXPO_PUBLIC_API_URL||"http://localhost:8000/api/v1";
export default function App(){
 const [job,setJob]=useState("Python Developer"),[category,setCategory]=useState("technical"),[items,setItems]=useState([]);
 async function load(){try{const r=await fetch(`${API}/interviews`);if(r.ok)setItems(await r.json())}catch{}}
 useEffect(()=>{load()},[]);
 async function create(){try{const r=await fetch(`${API}/interviews`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({mode:"practice",category,interaction_mode:"text",job_title:job,experience_level:"mid",duration_minutes:30,skills:["Problem solving"]})});const d=await r.json();if(!r.ok)throw Error(d.detail||"Failed");Alert.alert("Interview created",d.id);load()}catch(e){Alert.alert("Error",e.message)}}
 return <SafeAreaView style={s.page}><ScrollView contentContainerStyle={s.content}><Text style={s.title}>AI Interview Agent</Text><Text style={s.muted}>30-minute interview practice</Text><View style={s.card}><Text style={s.heading}>Create interview</Text><Text>Job title</Text><TextInput style={s.input} value={job} onChangeText={setJob}/><Text>Category: technical / hr / managerial / mixed</Text><TextInput style={s.input} value={category} onChangeText={setCategory}/><Button title="Create interview" onPress={create}/></View><View style={s.card}><Text style={s.heading}>Recent interviews</Text>{items.map(x=><Text key={x.id} style={s.item}>{x.job_title} · {x.status}</Text>)}<Button title="Refresh" onPress={load}/></View></ScrollView></SafeAreaView>
}
const s=StyleSheet.create({page:{flex:1,backgroundColor:"#f5f7fb"},content:{padding:20,gap:16},title:{fontSize:28,fontWeight:"700",color:"#172033"},muted:{color:"#687386"},card:{backgroundColor:"white",padding:18,borderRadius:14,gap:10},heading:{fontSize:19,fontWeight:"700"},input:{borderWidth:1,borderColor:"#d8deea",borderRadius:8,padding:10},item:{paddingVertical:8,color:"#26334a"}});
