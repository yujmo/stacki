# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

PKGROOT		= /var/www/html/doc
ROLLROOT	= ../..
DEPENDS.FILES	= $(wildcard *.rst */*.rst)

SPHINXDIR = $(STACKBUILD)/src/roll/etc/doc/sphinx/

include $(STACKBUILD)/etc/CCRules.mk
include $(SPHINXDIR)/sphinx.mk

GENRCLDOCS = $(STACKBUILD)/src/roll/etc/doc/genrcldocs


settings.py:
	@echo 'sys.path.append("$(PY.STACK)")'	>  $@
	@echo "release = \"`echo $(RELEASE) |tr _ -`\"" >> $@
	@echo 'copyright = "$(COPYRIGHT)"'	>> $@
	@echo 'master_doc = "index"'		>> $@
	@echo 'version = "$(VERSION)"'		>> $@
	@echo 'html_show_copyright = False'	>> $@

rcl:
	$(GENRCLDOCS) $(ROLL) sphinx

prep:: settings.py conf.py macros.rst _static

conf.py macros.rst _static:
	cp -rf $(SPHINXDIR)/$@ $(CURDIR)

build: prep rcl html

install::
	mkdir -p $(ROOT)/$(PKGROOT)/$(NAME)
	install -m 0644 _build/latex/*.pdf $(ROOT)/$(PKGROOT)/$(NAME)/
	install -m 0644 _build/epub/*.epub $(ROOT)/$(PKGROOT)/$(NAME)/
	(								\
		cd _build/html;						\
		find . | cpio -pduv $(ROOT)/$(PKGROOT)/$(NAME);		\
	)

clean::
	rm -rf cli
	rm -rf _build
	rm -rf _static
	rm -rf conf.py
	rm -rf macros.rst
	rm -f settings.py