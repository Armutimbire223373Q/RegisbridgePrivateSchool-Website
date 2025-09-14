import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  CreditCard, 
  Smartphone, 
  Building2, 
  DollarSign, 
  CheckCircle, 
  AlertCircle,
  Download,
  Eye,
  Clock
} from 'lucide-react'

interface PaymentMethod {
  id: string
  name: string
  description: string
  icon: string
  enabled: boolean
}

interface Payment {
  id: number
  invoice_id: number
  amount: number
  payment_method: string
  gateway: string
  transaction_id: string
  status: string
  created_at: string
  gateway_response?: any
}

interface Invoice {
  id: number
  invoice_number: string
  amount: number
  status: string
  due_date: string
  student_name: string
  description: string
}

const Payment: React.FC = () => {
  const { user } = useAuth()
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [payments, setPayments] = useState<Payment[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [selectedMethod, setSelectedMethod] = useState('')
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      // Simulate API calls
      setTimeout(() => {
        setPaymentMethods([
          {
            id: 'innbucks',
            name: 'InnBucks',
            description: 'Pay with InnBucks wallet',
            icon: '💳',
            enabled: true
          },
          {
            id: 'bank_transfer',
            name: 'Bank Transfer',
            description: 'Direct bank transfer',
            icon: '🏦',
            enabled: true
          },
          {
            id: 'ecocash',
            name: 'EcoCash',
            description: 'Pay with EcoCash mobile money',
            icon: '📱',
            enabled: true
          },
          {
            id: 'cash',
            name: 'Cash Payment',
            description: 'Pay at school office',
            icon: '💵',
            enabled: true
          }
        ])

        setInvoices([
          {
            id: 1,
            invoice_number: 'INV-2024-001',
            amount: 500.00,
            status: 'PENDING',
            due_date: '2024-02-15',
            student_name: 'Michael Brown',
            description: 'Tuition Fee - Term 1'
          },
          {
            id: 2,
            invoice_number: 'INV-2024-002',
            amount: 150.00,
            status: 'PENDING',
            due_date: '2024-02-20',
            student_name: 'Michael Brown',
            description: 'Library Fee'
          },
          {
            id: 3,
            invoice_number: 'INV-2024-003',
            amount: 300.00,
            status: 'PAID',
            due_date: '2024-01-15',
            student_name: 'Michael Brown',
            description: 'Boarding Fee'
          }
        ])

        setPayments([
          {
            id: 1,
            invoice_id: 3,
            amount: 300.00,
            payment_method: 'INNBUCKS',
            gateway: 'INNBUCKS',
            transaction_id: 'INN20240115143022',
            status: 'COMPLETED',
            created_at: '2024-01-15T14:30:22Z'
          },
          {
            id: 2,
            invoice_id: 2,
            amount: 150.00,
            payment_method: 'ECOCASH',
            gateway: 'ECOCASH',
            transaction_id: 'ECO20240120102015',
            status: 'PENDING',
            created_at: '2024-01-20T10:20:15Z'
          }
        ])

        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const handlePayment = async (method: string, invoice: Invoice) => {
    setProcessing(true)
    
    try {
      // Simulate payment processing
      setTimeout(() => {
        const newPayment: Payment = {
          id: Date.now(),
          invoice_id: invoice.id,
          amount: invoice.amount,
          payment_method: method.toUpperCase(),
          gateway: method.toUpperCase(),
          transaction_id: `${method.toUpperCase()}${Date.now()}`,
          status: 'COMPLETED',
          created_at: new Date().toISOString()
        }
        
        setPayments(prev => [newPayment, ...prev])
        setInvoices(prev => 
          prev.map(inv => 
            inv.id === invoice.id 
              ? { ...inv, status: 'PAID' }
              : inv
          )
        )
        
        setShowPaymentModal(false)
        setProcessing(false)
      }, 2000)
    } catch (error) {
      console.error('Payment error:', error)
      setProcessing(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'PAID':
        return 'bg-green-100 text-green-800'
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800'
      case 'FAILED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'PAID':
        return <CheckCircle className="h-4 w-4" />
      case 'PENDING':
        return <Clock className="h-4 w-4" />
      case 'FAILED':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getMethodIcon = (method: string) => {
    switch (method) {
      case 'innbucks':
        return <CreditCard className="h-6 w-6" />
      case 'bank_transfer':
        return <Building2 className="h-6 w-6" />
      case 'ecocash':
        return <Smartphone className="h-6 w-6" />
      case 'cash':
        return <DollarSign className="h-6 w-6" />
      default:
        return <CreditCard className="h-6 w-6" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Payments & Fees</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your payments and view payment history
          </p>
        </div>
      </div>

      {/* Payment Methods */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Available Payment Methods
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {paymentMethods.map((method) => (
              <div
                key={method.id}
                className={`relative group bg-white p-6 border-2 rounded-lg cursor-pointer transition-all ${
                  method.enabled
                    ? 'border-gray-200 hover:border-blue-500 hover:shadow-md'
                    : 'border-gray-100 opacity-50 cursor-not-allowed'
                }`}
                onClick={() => method.enabled && setSelectedMethod(method.id)}
              >
                <div className="flex items-center justify-center mb-4">
                  {getMethodIcon(method.id)}
                </div>
                <h4 className="text-lg font-medium text-gray-900 text-center">
                  {method.name}
                </h4>
                <p className="text-sm text-gray-500 text-center mt-2">
                  {method.description}
                </p>
                {!method.enabled && (
                  <div className="absolute inset-0 bg-gray-100 bg-opacity-50 rounded-lg flex items-center justify-center">
                    <span className="text-sm text-gray-500">Coming Soon</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Outstanding Invoices */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Outstanding Invoices
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Invoice
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {invoices.filter(inv => inv.status === 'PENDING').map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${invoice.amount.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(invoice.due_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(invoice.status)}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => {
                          setSelectedInvoice(invoice)
                          setShowPaymentModal(true)
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Pay Now
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Payment History */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Payment History
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Transaction ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {payments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {payment.transaction_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${payment.amount.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {payment.payment_method}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(payment.status)}`}>
                        {getStatusIcon(payment.status)}
                        <span className="ml-1">{payment.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(payment.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900 mr-4">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="text-gray-600 hover:text-gray-900">
                        <Download className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && selectedInvoice && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowPaymentModal(false)} />
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Pay Invoice: {selectedInvoice.invoice_number}
                </h3>
                <div className="mb-4">
                  <p className="text-sm text-gray-600">Amount: <span className="font-semibold">${selectedInvoice.amount.toFixed(2)}</span></p>
                  <p className="text-sm text-gray-600">Description: {selectedInvoice.description}</p>
                </div>
                <div className="space-y-3">
                  {paymentMethods.filter(m => m.enabled).map((method) => (
                    <button
                      key={method.id}
                      onClick={() => handlePayment(method.id, selectedInvoice)}
                      disabled={processing}
                      className="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                    >
                      <div className="flex items-center">
                        {getMethodIcon(method.id)}
                        <div className="ml-3 text-left">
                          <p className="text-sm font-medium text-gray-900">{method.name}</p>
                          <p className="text-sm text-gray-500">{method.description}</p>
                        </div>
                      </div>
                      {processing && selectedMethod === method.id && (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-gray-600 text-base font-medium text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowPaymentModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Payment