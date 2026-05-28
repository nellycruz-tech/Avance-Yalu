from rest_framework import serializers
from .models import Rol, Usuario, Direccion


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = [
            'id', 'departamento', 'provincia', 'distrito',
            'direccion_detallada', 'referencia', 'es_principal'
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    direcciones = DireccionSerializer(many=True, read_only=True)

    class Meta:
        model = Usuario
        fields =[
            'id', 'firebase_uid', 'nombres', 'apellidos', 'alias', 
            'email', 'telefono', 'rol', 'estado',
            'created_at', 'direcciones'
        ]
        read_only_fields = ['firebase_uid', 'created_at', 'email']


class FirebaseLoginSerializer(serializers.Serializer):
    firebase_token = serializers.CharField()
