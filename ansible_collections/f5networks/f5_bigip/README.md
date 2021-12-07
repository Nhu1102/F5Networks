#Ansible Collection f5_bigip

A collection focusing on managing F5 BIG-IP/BIG-IQ through declarative APIs such as AS3, DO, TS, and CFE. 
The collection does include key imperative modules as well for managing some resources and operational tasks 
that are not part of declarative workflows. These would include actions such as saving config, backing up config, 
uploading security policies, uploading crts/keys, gathering info, etc.

**Note that this Collection is not currently intended to replace the existing** [f5_modules] **Collection.**

##Python Version
This collection is supported on Python 3.6 and above.

## Important Information
This branch is an experimental branch of f5_bigip collection, which is meant as a preview. 
It is focused on incubating Ansible solutions for SSL Orchestrator feature of BIG-IP.
When finished the contents of this branch will be incorpoated into f5_bigip collection.
Until that time breaking changes might be introduced into this branch and usage of this branch is considered an agreement 
to below disclaimer.

## Disclaimer

Limitation on Liability Provision of any Software under this Agreement is experimental and shall not create any obligation for F5 Networks to continue to develop, productize, support, repair, offer for sale or in any other way continue to provide or develop Software either to Licensee or to any other party

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

##Bugs, Issues
   
Please file any bugs, questions, or enhancement requests by using [ansible_issues]. For details, see [ansiblehelp].

##Your ideas


What types of modules do you want created? If you have a use case and can sufficiently describe the behavior 
you want to see, open an issue and we will hammer out the details.

If you've got the time, consider sending an email that introduces yourself and what you do. 
We love hearing about how you're using the F5_BIGIP collection for Ansible.

> **_NOTE:_** **This repository is a mirror, only issues submissions are accepted.**

- Wojciech Wypior and the F5 team - solutionsfeedback@f5.com

##Copyright

Copyright 2021 F5 Networks Inc.


##License

####GPL V3

This License does not grant permission to use the trade names, trademarks, service marks, or product names of the 
Licensor, except as required for reasonable and customary use in describing the origin of the Work.

See [License].

####Contributor License Agreement
Individuals or business entities who contribute to this project must complete and submit the 
[F5 Contributor License Agreement] to ***Ansible_CLA@f5.com*** prior to their code submission 
being included in this project.


[repoinstall]: https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-a-collection-from-a-git-repository
[f5_modules]: https://galaxy.ansible.com/f5networks/f5_modules
[dailybuild]: https://f5-ansible.s3.amazonaws.com/collections/f5networks-f5_bigip-devel.tar.gz
[License]: https://github.com/f5devcentral/f5-ansible-bigip/blob/master/COPYING
[ansible_issues]: https://github.com/F5Networks/f5-ansible-bigip/issues
[ansiblehelp]: http://clouddocs.f5.com/products/orchestration/ansible/devel/
[F5 Contributor License Agreement]: http://clouddocs.f5.com/products/orchestration/ansible/devel/usage/contributor.html