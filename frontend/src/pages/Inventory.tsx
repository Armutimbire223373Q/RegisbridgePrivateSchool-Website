import React, { useState, useEffect } from 'react'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Eye, 
  Package, 
  AlertTriangle,
  CheckCircle,
  Filter,
  Download
} from 'lucide-react'

interface InventoryItem {
  id: number
  name: string
  description: string
  category: string
  quantity: number
  min_quantity: number
  unit_price: number
  total_value: number
  supplier: string
  location: string
  status: 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK'
  last_updated: string
  created_at: string
}

const Inventory: React.FC = () => {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null)
  const [showViewModal, setShowViewModal] = useState(false)

  useEffect(() => {
    fetchInventoryItems()
  }, [])

  const fetchInventoryItems = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        setItems([
          {
            id: 1,
            name: "Mathematics Textbooks - Grade 7",
            description: "Complete set of mathematics textbooks for grade 7 students",
            category: "Books",
            quantity: 45,
            min_quantity: 20,
            unit_price: 25.00,
            total_value: 1125.00,
            supplier: "Educational Publishers Ltd",
            location: "Library - Section A",
            status: "IN_STOCK",
            last_updated: "2024-01-15T10:00:00Z",
            created_at: "2024-01-01T00:00:00Z"
          },
          {
            id: 2,
            name: "Laboratory Microscopes",
            description: "High-quality microscopes for science laboratory",
            category: "Equipment",
            quantity: 8,
            min_quantity: 10,
            unit_price: 150.00,
            total_value: 1200.00,
            supplier: "Science Equipment Co",
            location: "Science Lab - Room 2",
            status: "LOW_STOCK",
            last_updated: "2024-01-14T14:30:00Z",
            created_at: "2024-01-01T00:00:00Z"
          },
          {
            id: 3,
            name: "School Uniforms - Boys",
            description: "Complete school uniform set for boys (shirt, pants, tie)",
            category: "Uniforms",
            quantity: 0,
            min_quantity: 15,
            unit_price: 35.00,
            total_value: 0.00,
            supplier: "Uniform Suppliers Inc",
            location: "Store Room - Uniform Section",
            status: "OUT_OF_STOCK",
            last_updated: "2024-01-10T09:15:00Z",
            created_at: "2024-01-01T00:00:00Z"
          },
          {
            id: 4,
            name: "Sports Equipment - Footballs",
            description: "Official size footballs for sports activities",
            category: "Sports",
            quantity: 12,
            min_quantity: 8,
            unit_price: 20.00,
            total_value: 240.00,
            supplier: "Sports Equipment Ltd",
            location: "Sports Store - Equipment Room",
            status: "IN_STOCK",
            last_updated: "2024-01-12T16:45:00Z",
            created_at: "2024-01-01T00:00:00Z"
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching inventory items:', error)
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this inventory item?')) {
      setItems(items.filter(item => item.id !== id))
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'IN_STOCK':
        return 'bg-green-100 text-green-800'
      case 'LOW_STOCK':
        return 'bg-yellow-100 text-yellow-800'
      case 'OUT_OF_STOCK':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'IN_STOCK':
        return <CheckCircle className="h-4 w-4" />
      case 'LOW_STOCK':
        return <AlertTriangle className="h-4 w-4" />
      case 'OUT_OF_STOCK':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Package className="h-4 w-4" />
    }
  }

  const filteredItems = items.filter(item => {
    const matchesSearch = 
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.supplier.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesCategory = filterCategory === '' || item.category === filterCategory
    const matchesStatus = filterStatus === '' || item.status === filterStatus
    
    return matchesSearch && matchesCategory && matchesStatus
  })

  const categories = ['All', 'Books', 'Equipment', 'Uniforms', 'Sports', 'Supplies']
  const statuses = ['All', 'IN_STOCK', 'LOW_STOCK', 'OUT_OF_STOCK']

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
          <h1 className="text-2xl font-semibold text-gray-900">Inventory Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage school inventory, equipment, and supplies
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:w-auto"
            onClick={() => setShowAddModal(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Item
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-blue-500">
                  <Package className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Items
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">{items.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-green-500">
                  <CheckCircle className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    In Stock
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {items.filter(item => item.status === 'IN_STOCK').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-yellow-500">
                  <AlertTriangle className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Low Stock
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {items.filter(item => item.status === 'LOW_STOCK').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-red-500">
                  <AlertTriangle className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Out of Stock
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {items.filter(item => item.status === 'OUT_OF_STOCK').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search
            </label>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                name="search"
                id="search"
                className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
                placeholder="Search items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700">
              Category
            </label>
            <select
              id="category"
              name="category"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              {categories.map(category => (
                <option key={category} value={category === 'All' ? '' : category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="status"
              name="status"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              {statuses.map(status => (
                <option key={status} value={status === 'All' ? '' : status}>
                  {status.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {item.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {item.description}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>
                        <div className="font-medium">{item.quantity}</div>
                        <div className="text-gray-500">Min: {item.min_quantity}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                        {getStatusIcon(item.status)}
                        <span className="ml-1">{item.status.replace('_', ' ')}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>
                        <div className="font-medium">${item.total_value.toFixed(2)}</div>
                        <div className="text-gray-500">${item.unit_price.toFixed(2)} each</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.location}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setSelectedItem(item)
                            setShowViewModal(true)
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedItem(item)
                            // Handle edit
                          }}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* View Item Modal */}
      {showViewModal && selectedItem && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowViewModal(false)} />
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                      Item Details
                    </h3>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-500">Name</label>
                          <p className="text-sm text-gray-900">{selectedItem.name}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Category</label>
                          <p className="text-sm text-gray-900">{selectedItem.category}</p>
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Description</label>
                        <p className="text-sm text-gray-900">{selectedItem.description}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-500">Quantity</label>
                          <p className="text-sm text-gray-900">{selectedItem.quantity} (Min: {selectedItem.min_quantity})</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Status</label>
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedItem.status)}`}>
                            {getStatusIcon(selectedItem.status)}
                            <span className="ml-1">{selectedItem.status.replace('_', ' ')}</span>
                          </span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-500">Unit Price</label>
                          <p className="text-sm text-gray-900">${selectedItem.unit_price.toFixed(2)}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Total Value</label>
                          <p className="text-sm text-gray-900">${selectedItem.total_value.toFixed(2)}</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-500">Supplier</label>
                          <p className="text-sm text-gray-900">{selectedItem.supplier}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Location</label>
                          <p className="text-sm text-gray-900">{selectedItem.location}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowViewModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Inventory
