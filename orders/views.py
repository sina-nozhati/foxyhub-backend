from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q

from .models import Order, Payment
from .serializers import OrderSerializer, OrderCreateSerializer, PaymentSerializer
from core.services.cryptomus import CryptomusClient


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return orders for the current user.
        """
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        """
        Create a new order.
        """
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        """
        Create a payment for an order.
        """
        order = self.get_object()
        
        # Check if order is already paid
        if order.status != Order.OrderStatus.PENDING:
            return Response(
                {"detail": "Cannot create payment for non-pending order."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get payment method from request
        payment_method = request.data.get('payment_method')
        if not payment_method:
            return Response(
                {"detail": "Payment method is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment based on method
        if payment_method == Payment.PaymentMethod.CRYPTO:
            # Create Cryptomus payment
            cryptomus_client = CryptomusClient()
            callback_url = request.build_absolute_uri(f'/api/v1/orders/webhook/')
            
            try:
                payment_data = cryptomus_client.create_payment(
                    amount=float(order.total_amount),
                    currency='USD',
                    order_id=str(order.id),
                    description=f"Payment for order {order.id}",
                    callback_url=callback_url
                )
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method=Payment.PaymentMethod.CRYPTO,
                    payment_details=payment_data
                )
                
                return Response({
                    "payment": PaymentSerializer(payment).data,
                    "payment_url": payment_data.get('result', {}).get('url')
                })
                
            except Exception as e:
                return Response(
                    {"detail": f"Error creating payment: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"detail": "Unsupported payment method."},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentWebhookView(generics.GenericAPIView):
    """
    View for handling payment webhooks from Cryptomus.
    """
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request, *args, **kwargs):
        """
        Handle webhook from Cryptomus.
        """
        # In a real implementation, you would verify the webhook signature
        # and update the order status based on the payment status
        
        # For now, we'll just return a success response
        return Response({"status": "success"})

