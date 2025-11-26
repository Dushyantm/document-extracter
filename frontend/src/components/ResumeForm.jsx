import { useState, useEffect } from 'react';
import { User, GraduationCap, Briefcase, Code, Plus, Trash2 } from 'lucide-react';

export default function ResumeForm({ data }) {
  // Initialize with default empty values if data is missing
  const [formData, setFormData] = useState({
    contact: data?.contact || { first_name: '', last_name: '', email: '', phone: '', city: '', state: '' },
    education: data?.education && data.education.length > 0 ? data.education : [{ degree: '', field_of_study: '', institution: '', graduation_year: '' }],
    work_experience: data?.work_experience && data.work_experience.length > 0 ? data.work_experience : [{ job_title: '', company: '', start_date: '', end_date: '', description: [] }],
    skills: data?.skills || [],
  });

  // Update form when new data is received
  useEffect(() => {
    if (data) {
      setFormData({
        contact: data.contact || { first_name: '', last_name: '', email: '', phone: '', city: '', state: '' },
        education: data.education && data.education.length > 0 ? data.education : [{ degree: '', field_of_study: '', institution: '', graduation_year: '' }],
        work_experience: data.work_experience && data.work_experience.length > 0 ? data.work_experience : [{ job_title: '', company: '', start_date: '', end_date: '', description: [] }],
        skills: data.skills || [],
      });
    }
  }, [data]);

  const updateContact = (field, value) => {
    setFormData({
      ...formData,
      contact: {
        ...formData.contact,
        [field]: value,
      },
    });
  };

  const updateEducation = (index, field, value) => {
    const newEducation = [...formData.education];
    newEducation[index] = {
      ...newEducation[index],
      [field]: value,
    };
    setFormData({ ...formData, education: newEducation });
  };

  const addEducation = () => {
    setFormData({
      ...formData,
      education: [
        ...formData.education,
        { degree: '', field_of_study: '', institution: '', graduation_year: '' },
      ],
    });
  };

  const removeEducation = (index) => {
    setFormData({
      ...formData,
      education: formData.education.filter((_, i) => i !== index),
    });
  };

  const updateExperience = (index, field, value) => {
    const newExperience = [...formData.work_experience];
    newExperience[index] = {
      ...newExperience[index],
      [field]: value,
    };
    setFormData({ ...formData, work_experience: newExperience });
  };

  const addExperience = () => {
    setFormData({
      ...formData,
      work_experience: [
        ...formData.work_experience,
        { job_title: '', company: '', start_date: '', end_date: '', description: [] },
      ],
    });
  };

  const removeExperience = (index) => {
    setFormData({
      ...formData,
      work_experience: formData.work_experience.filter((_, i) => i !== index),
    });
  };

  const updateSkills = (value) => {
    const skillsArray = value.split(',').map((s) => s.trim()).filter((s) => s);
    setFormData({ ...formData, skills: skillsArray });
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="bg-blue-600 px-6 py-4 border-b border-blue-700">
        <h2 className="text-white text-xl font-semibold">Extracted Information</h2>
        <p className="text-blue-100 text-sm mt-1">Review and edit the parsed data</p>
      </div>

      {/* Form Content */}
      <div className="flex-1 overflow-auto p-6 space-y-8">
        {/* Contact Information */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <User className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Contact Information</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name
              </label>
              <input
                type="text"
                value={formData.contact.first_name}
                onChange={(e) => updateContact('first_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Name
              </label>
              <input
                type="text"
                value={formData.contact.last_name}
                onChange={(e) => updateContact('last_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.contact.email}
                onChange={(e) => updateContact('email', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                type="tel"
                value={formData.contact.phone}
                onChange={(e) => updateContact('phone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                value={formData.contact.city}
                onChange={(e) => updateContact('city', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State
              </label>
              <input
                type="text"
                value={formData.contact.state}
                onChange={(e) => updateContact('state', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* Education */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Education</h3>
            </div>
            <button
              onClick={addEducation}
              className="flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
          <div className="space-y-4">
            {formData.education.map((edu, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg relative">
                {formData.education.length > 1 && (
                  <button
                    onClick={() => removeEducation(index)}
                    className="absolute top-2 right-2 p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Degree
                    </label>
                    <input
                      type="text"
                      value={edu.degree}
                      onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Field of Study
                    </label>
                    <input
                      type="text"
                      value={edu.field_of_study}
                      onChange={(e) => updateEducation(index, 'field_of_study', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Institution
                    </label>
                    <input
                      type="text"
                      value={edu.institution}
                      onChange={(e) => updateEducation(index, 'institution', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Graduation Year
                    </label>
                    <input
                      type="text"
                      value={edu.graduation_year}
                      onChange={(e) => updateEducation(index, 'graduation_year', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Work Experience */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Work Experience</h3>
            </div>
            <button
              onClick={addExperience}
              className="flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
          <div className="space-y-4">
            {formData.work_experience.map((exp, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg relative">
                {formData.work_experience.length > 1 && (
                  <button
                    onClick={() => removeExperience(index)}
                    className="absolute top-2 right-2 p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Job Title
                    </label>
                    <input
                      type="text"
                      value={exp.job_title}
                      onChange={(e) => updateExperience(index, 'job_title', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company
                    </label>
                    <input
                      type="text"
                      value={exp.company}
                      onChange={(e) => updateExperience(index, 'company', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Date
                    </label>
                    <input
                      type="text"
                      value={exp.start_date}
                      onChange={(e) => updateExperience(index, 'start_date', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Date
                    </label>
                    <input
                      type="text"
                      value={exp.end_date}
                      onChange={(e) => updateExperience(index, 'end_date', e.target.value)}
                      placeholder="Present"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={exp.description.join('\n')}
                      onChange={(e) => updateExperience(index, 'description', e.target.value.split('\n'))}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Skills */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Code className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Skills</h3>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Skills (comma-separated)
            </label>
            <textarea
              value={formData.skills.join(', ')}
              onChange={(e) => updateSkills(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
        </section>
      </div>
    </div>
  );
}
