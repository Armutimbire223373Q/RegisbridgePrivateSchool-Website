import React, { useState } from 'react'
import { 
  User, 
  FileText, 
  Send,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'

interface AdmissionForm {
  // Personal Information
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  nationality: string
  
  // Contact Information
  email: string
  phone_number: string
  address: string
  city: string
  postal_code: string
  
  // Academic Information
  previous_school: string
  previous_grade: string
  intended_grade: string
  
  // Parent/Guardian Information
  parent_name: string
  parent_phone: string
  parent_email: string
  parent_relationship: string
  
  // Additional Information
  special_needs: string
  medical_conditions: string
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relationship: string
  
  // Financial Information
  scholarship_requested: boolean
  scholarship_amount: string
  financial_aid_notes: string
  
  // Boarding Information
  boarding_requested: boolean
  boarding_type: string
  special_dietary_requirements: string
}

const Admissions: React.FC = () => {
  const [formData, setFormData] = useState<AdmissionForm>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    nationality: 'Kenyan',
    email: '',
    phone_number: '',
    address: '',
    city: '',
    postal_code: '',
    previous_school: '',
    previous_grade: '',
    intended_grade: '',
    parent_name: '',
    parent_phone: '',
    parent_email: '',
    parent_relationship: '',
    special_needs: '',
    medical_conditions: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relationship: '',
    scholarship_requested: false,
    scholarship_amount: '',
    financial_aid_notes: '',
    boarding_requested: false,
    boarding_type: '',
    special_dietary_requirements: ''
  })
  
  const [currentStep, setCurrentStep] = useState(1)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [errors, setErrors] = useState<{[key: string]: string}>({})

  const steps = [
    { id: 1, name: 'Personal Information', icon: User },
    { id: 2, name: 'Academic Information', icon: FileText },
    { id: 3, name: 'Parent/Guardian', icon: User },
    { id: 4, name: 'Additional Information', icon: FileText },
    { id: 5, name: 'Review & Submit', icon: Send }
  ]

  const handleInputChange = (field: keyof AdmissionForm, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateStep = (step: number): boolean => {
    const newErrors: {[key: string]: string} = {}

    switch (step) {
      case 1:
        if (!formData.first_name) newErrors.first_name = 'First name is required'
        if (!formData.last_name) newErrors.last_name = 'Last name is required'
        if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required'
        if (!formData.gender) newErrors.gender = 'Gender is required'
        if (!formData.email) newErrors.email = 'Email is required'
        if (!formData.phone_number) newErrors.phone_number = 'Phone number is required'
        break
      case 2:
        if (!formData.previous_school) newErrors.previous_school = 'Previous school is required'
        if (!formData.intended_grade) newErrors.intended_grade = 'Intended grade is required'
        break
      case 3:
        if (!formData.parent_name) newErrors.parent_name = 'Parent/Guardian name is required'
        if (!formData.parent_phone) newErrors.parent_phone = 'Parent/Guardian phone is required'
        if (!formData.parent_email) newErrors.parent_email = 'Parent/Guardian email is required'
        break
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length))
    }
  }

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1))
  }

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return

    setSubmitting(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      setSubmitted(true)
    } catch (error) {
      console.error('Error submitting application:', error)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Application Submitted!
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Your application has been received. We will review it and contact you soon.
            </p>
            <div className="mt-8 space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <Clock className="h-5 w-5 text-blue-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      What's Next?
                    </h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <ul className="list-disc list-inside space-y-1">
                        <li>We'll review your application within 5-7 business days</li>
                        <li>You'll receive an email with your application number</li>
                        <li>We may contact you for additional information</li>
                        <li>Final decision will be communicated via email</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Submit Another Application
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900">
            Admission Application
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Join Regisbridge Private School - Primary & Secondary Education with Boarding
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <nav aria-label="Progress">
            <ol className="flex items-center justify-center space-x-8">
              {steps.map((step, stepIdx) => {
                const Icon = step.icon
                return (
                  <li key={step.name} className="relative">
                    {step.id < currentStep ? (
                      <div className="flex items-center">
                        <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-blue-600 rounded-full">
                          <CheckCircle className="w-6 h-6 text-white" />
                        </div>
                        <div className="ml-4 min-w-0">
                          <div className="text-sm font-medium text-blue-600">{step.name}</div>
                        </div>
                      </div>
                    ) : step.id === currentStep ? (
                      <div className="flex items-center">
                        <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-blue-600 rounded-full">
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <div className="ml-4 min-w-0">
                          <div className="text-sm font-medium text-blue-600">{step.name}</div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center">
                        <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-gray-300 rounded-full">
                          <Icon className="w-6 h-6 text-gray-500" />
                        </div>
                        <div className="ml-4 min-w-0">
                          <div className="text-sm font-medium text-gray-500">{step.name}</div>
                        </div>
                      </div>
                    )}
                    {stepIdx !== steps.length - 1 && (
                      <div className="hidden sm:block absolute top-5 left-10 w-full h-0.5 bg-gray-300" />
                    )}
                  </li>
                )
              })}
            </ol>
          </nav>
        </div>

        {/* Form Content */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            {/* Step 1: Personal Information */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name *
                    </label>
                    <input
                      type="text"
                      value={formData.first_name}
                      onChange={(e) => handleInputChange('first_name', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.first_name ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter first name"
                    />
                    {errors.first_name && (
                      <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      value={formData.last_name}
                      onChange={(e) => handleInputChange('last_name', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.last_name ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter last name"
                    />
                    {errors.last_name && (
                      <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date of Birth *
                    </label>
                    <input
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.date_of_birth ? 'border-red-300' : 'border-gray-300'
                      }`}
                    />
                    {errors.date_of_birth && (
                      <p className="mt-1 text-sm text-red-600">{errors.date_of_birth}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Gender *
                    </label>
                    <select
                      value={formData.gender}
                      onChange={(e) => handleInputChange('gender', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.gender ? 'border-red-300' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                    {errors.gender && (
                      <p className="mt-1 text-sm text-red-600">{errors.gender}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nationality
                    </label>
                    <input
                      type="text"
                      value={formData.nationality}
                      onChange={(e) => handleInputChange('nationality', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter nationality"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.email ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter email address"
                    />
                    {errors.email && (
                      <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      value={formData.phone_number}
                      onChange={(e) => handleInputChange('phone_number', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.phone_number ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter phone number"
                    />
                    {errors.phone_number && (
                      <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Address
                    </label>
                    <input
                      type="text"
                      value={formData.address}
                      onChange={(e) => handleInputChange('address', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter address"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      City
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => handleInputChange('city', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter city"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Postal Code
                    </label>
                    <input
                      type="text"
                      value={formData.postal_code}
                      onChange={(e) => handleInputChange('postal_code', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter postal code"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Academic Information */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Academic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Previous School *
                    </label>
                    <input
                      type="text"
                      value={formData.previous_school}
                      onChange={(e) => handleInputChange('previous_school', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.previous_school ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter previous school name"
                    />
                    {errors.previous_school && (
                      <p className="mt-1 text-sm text-red-600">{errors.previous_school}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Previous Grade
                    </label>
                    <input
                      type="text"
                      value={formData.previous_grade}
                      onChange={(e) => handleInputChange('previous_grade', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter previous grade"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Intended Grade *
                    </label>
                    <select
                      value={formData.intended_grade}
                      onChange={(e) => handleInputChange('intended_grade', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.intended_grade ? 'border-red-300' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select intended grade</option>
                      <optgroup label="Primary Level">
                        <option value="Grade 1">Grade 1</option>
                        <option value="Grade 2">Grade 2</option>
                        <option value="Grade 3">Grade 3</option>
                        <option value="Grade 4">Grade 4</option>
                        <option value="Grade 5">Grade 5</option>
                        <option value="Grade 6">Grade 6</option>
                        <option value="Grade 7">Grade 7</option>
                      </optgroup>
                      <optgroup label="Secondary Level">
                        <option value="Form 1">Form 1</option>
                        <option value="Form 2">Form 2</option>
                        <option value="Form 3">Form 3</option>
                        <option value="Form 4">Form 4</option>
                      </optgroup>
                    </select>
                    {errors.intended_grade && (
                      <p className="mt-1 text-sm text-red-600">{errors.intended_grade}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Parent/Guardian Information */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Parent/Guardian Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Parent/Guardian Name *
                    </label>
                    <input
                      type="text"
                      value={formData.parent_name}
                      onChange={(e) => handleInputChange('parent_name', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.parent_name ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter parent/guardian name"
                    />
                    {errors.parent_name && (
                      <p className="mt-1 text-sm text-red-600">{errors.parent_name}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Relationship *
                    </label>
                    <select
                      value={formData.parent_relationship}
                      onChange={(e) => handleInputChange('parent_relationship', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select relationship</option>
                      <option value="Father">Father</option>
                      <option value="Mother">Mother</option>
                      <option value="Guardian">Guardian</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      value={formData.parent_phone}
                      onChange={(e) => handleInputChange('parent_phone', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.parent_phone ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter phone number"
                    />
                    {errors.parent_phone && (
                      <p className="mt-1 text-sm text-red-600">{errors.parent_phone}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      value={formData.parent_email}
                      onChange={(e) => handleInputChange('parent_email', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.parent_email ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Enter email address"
                    />
                    {errors.parent_email && (
                      <p className="mt-1 text-sm text-red-600">{errors.parent_email}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Additional Information */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Additional Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Emergency Contact Name
                    </label>
                    <input
                      type="text"
                      value={formData.emergency_contact_name}
                      onChange={(e) => handleInputChange('emergency_contact_name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter emergency contact name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Emergency Contact Phone
                    </label>
                    <input
                      type="tel"
                      value={formData.emergency_contact_phone}
                      onChange={(e) => handleInputChange('emergency_contact_phone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter emergency contact phone"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Emergency Contact Relationship
                    </label>
                    <input
                      type="text"
                      value={formData.emergency_contact_relationship}
                      onChange={(e) => handleInputChange('emergency_contact_relationship', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter relationship"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Medical Conditions
                    </label>
                    <textarea
                      value={formData.medical_conditions}
                      onChange={(e) => handleInputChange('medical_conditions', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter any medical conditions"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Special Needs
                    </label>
                    <textarea
                      value={formData.special_needs}
                      onChange={(e) => handleInputChange('special_needs', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter any special needs"
                    />
                  </div>
                </div>
                
                {/* Boarding Information */}
                <div className="border-t pt-6">
                  <h4 className="text-md font-medium text-gray-900 mb-4">Boarding Services</h4>
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="boarding_requested"
                        checked={formData.boarding_requested}
                        onChange={(e) => handleInputChange('boarding_requested', e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="boarding_requested" className="ml-2 block text-sm text-gray-900">
                        Requesting boarding services
                      </label>
                    </div>
                    {formData.boarding_requested && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Boarding Type
                          </label>
                          <select
                            value={formData.boarding_type}
                            onChange={(e) => handleInputChange('boarding_type', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">Select boarding type</option>
                            <option value="Full Boarding">Full Boarding (7 days/week)</option>
                            <option value="Weekly Boarding">Weekly Boarding (Monday-Friday)</option>
                            <option value="Flexible Boarding">Flexible Boarding</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Special Dietary Requirements
                          </label>
                          <textarea
                            value={formData.special_dietary_requirements}
                            onChange={(e) => handleInputChange('special_dietary_requirements', e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Any special dietary needs or restrictions"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Financial Information */}
                <div className="border-t pt-6">
                  <h4 className="text-md font-medium text-gray-900 mb-4">Financial Information</h4>
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="scholarship_requested"
                        checked={formData.scholarship_requested}
                        onChange={(e) => handleInputChange('scholarship_requested', e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="scholarship_requested" className="ml-2 block text-sm text-gray-900">
                        Requesting scholarship or financial aid
                      </label>
                    </div>
                    {formData.scholarship_requested && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Scholarship Amount Requested
                          </label>
                          <input
                            type="text"
                            value={formData.scholarship_amount}
                            onChange={(e) => handleInputChange('scholarship_amount', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter amount"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Financial Aid Notes
                          </label>
                          <textarea
                            value={formData.financial_aid_notes}
                            onChange={(e) => handleInputChange('financial_aid_notes', e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Explain your financial situation"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 5: Review & Submit */}
            {currentStep === 5 && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Review Your Application</h3>
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-4">Personal Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div><strong>Name:</strong> {formData.first_name} {formData.last_name}</div>
                    <div><strong>Date of Birth:</strong> {formData.date_of_birth}</div>
                    <div><strong>Gender:</strong> {formData.gender}</div>
                    <div><strong>Email:</strong> {formData.email}</div>
                    <div><strong>Phone:</strong> {formData.phone_number}</div>
                    <div><strong>Nationality:</strong> {formData.nationality}</div>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-4">Academic Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div><strong>Previous School:</strong> {formData.previous_school}</div>
                    <div><strong>Previous Grade:</strong> {formData.previous_grade}</div>
                    <div><strong>Intended Grade:</strong> {formData.intended_grade}</div>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-4">Parent/Guardian Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div><strong>Name:</strong> {formData.parent_name}</div>
                    <div><strong>Relationship:</strong> {formData.parent_relationship}</div>
                    <div><strong>Phone:</strong> {formData.parent_phone}</div>
                    <div><strong>Email:</strong> {formData.parent_email}</div>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <AlertCircle className="h-5 w-5 text-blue-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800">
                        Important Notice
                      </h3>
                      <div className="mt-2 text-sm text-blue-700">
                        <p>By submitting this application, you agree to:</p>
                        <ul className="list-disc list-inside mt-1 space-y-1">
                          <li>Provide accurate information</li>
                          <li>Submit required documents within 7 days</li>
                          <li>Pay application fee if applicable</li>
                          <li>Attend interview if requested</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-6">
              <button
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              {currentStep < steps.length ? (
                <button
                  onClick={handleNext}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Next
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={submitting}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Submit Application'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Admissions
