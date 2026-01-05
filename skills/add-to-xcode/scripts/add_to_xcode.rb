#!/usr/bin/env ruby
# Add a file to the nearest Xcode project
#
# Usage: ruby add_to_xcode.rb <file_path>
#
# Requires: gem install xcodeproj

require 'xcodeproj'

file_path = ARGV[0]
abort "Usage: add_to_xcode.rb <file_path>" unless file_path
abort "File doesn't exist: #{file_path}" unless File.exist?(file_path)

# Find .xcodeproj in current dir or parents
def find_xcodeproj(start_dir)
  dir = File.expand_path(start_dir)
  loop do
    proj = Dir.glob(File.join(dir, '*.xcodeproj')).first
    return proj if proj
    parent = File.dirname(dir)
    break if parent == dir
    dir = parent
  end
  nil
end

project_file = find_xcodeproj('.')
abort "No .xcodeproj found" unless project_file

project = Xcodeproj::Project.open(project_file)
project_root = File.dirname(project_file)

# Make path relative to project root
relative_path = File.expand_path(file_path).sub("#{File.expand_path(project_root)}/", '')

# Build or find group hierarchy
dir = File.dirname(relative_path)
group = project.main_group

unless dir == '.'
  dir.split('/').each do |folder|
    existing = group[folder]
    if existing
      group = existing
    else
      group = group.new_group(folder, folder)
    end
  end
end

# Add file if not already present
filename = File.basename(relative_path)
unless group.files.any? { |f| f.path == filename }
  file_ref = group.new_file(relative_path)
  
  # Add to first target if source file
  if relative_path.match?(/\.(swift|m|mm|c|cpp)$/)
    target = project.targets.first
    target&.source_build_phase&.add_file_reference(file_ref)
    puts "✓ Added #{relative_path} to #{project_file} (target: #{target&.name})"
  else
    puts "✓ Added #{relative_path} to #{project_file}"
  end
else
  puts "⚠ File already in project: #{relative_path}"
end

project.save
